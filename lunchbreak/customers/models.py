import math
from decimal import Decimal

from business.models import Staff
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django_gocardless.config import CURRENCY_EUR, PAYMENT_STATUS_PAID_OUT
from django_gocardless.exceptions import DjangoGoCardlessException
from django_gocardless.models import Payment, RedirectFlow
from django_sms.exceptions import PinTimeout
from django_sms.models import Phone
from lunch.config import (COST_GROUP_ADDITIONS, COST_GROUP_BOTH, INPUT_SI_SET,
                          INPUT_SI_VARIABLE)
from lunch.exceptions import BadRequest, LinkingError, NoDeliveryToAddress
from lunch.models import AbstractAddress, BaseToken, Food, Ingredient, Store
from lunch.utils import timezone_for_store
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.mixins import CleanModelMixin
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import status
from rest_framework.response import Response

from .config import (GROUP_BILLING_SEPARATE, GROUP_BILLINGS,
                     INVITE_STATUS_ACCEPTED, INVITE_STATUS_WAITING,
                     INVITE_STATUSES, ORDER_STATUS_COMPLETED,
                     ORDER_STATUS_PLACED, ORDER_STATUS_SIGNALS, ORDER_STATUSES,
                     ORDER_STATUSES_ACTIVE, ORDER_STATUSES_ENDED,
                     PAYMENT_METHOD_CASH, PAYMENT_METHOD_GOCARDLESS,
                     PAYMENT_METHODS, RESERVATION_STATUS_DENIED,
                     RESERVATION_STATUS_PLACED, RESERVATION_STATUSES)
from .exceptions import (AlreadyMembership, AmountInvalid, CostCheckFailed,
                         InvalidStatusChange, MaxSeatsExceeded,
                         MinDaysExceeded, NoInvitePermissions, NoPaymentLink,
                         OnlinePaymentDisabled, PaymentLinkNotConfirmed,
                         UserDisabled)
from .managers import OrderedFoodManager, OrderManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.OneToOneField(
        'django_sms.Phone',
        on_delete=models.CASCADE,
        verbose_name=_('telefoonnummer'),
        help_text=_('Telefoonnummer.')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('e-mailadres'),
        help_text=_('E-mailadres.')
    )

    enabled = models.BooleanField(
        default=True,
        verbose_name=_('ingeschakeld'),
        help_text=_('Ingeschakeld.')
    )

    paymentlinks = models.ManyToManyField(
        Store,
        through='PaymentLink',
        through_fields=(
            'user',
            'store',
        ),
        blank=True,
        verbose_name=_('getekende mandaten'),
        help_text=_('Getekende mandaten.')
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Lunchbreak werknemer'),
        help_text=_(
            'Lunchbreak werknemer, dit geeft toegang tot het controle paneel.'
        )
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = [
        'name',
    ]

    objects = UserManager()

    class Meta:
        verbose_name = _('gebruiker')
        verbose_name_plural = _('gebruikers')

    def __str__(self):
        return '{name} {phone}'.format(
            name=self.name,
            phone=self.phone
        )

    def phone_clean(raw_value, model_instance):
        return Phone._meta.get_field('phone').clean(
            raw_value, model_instance
        )

    phone.clean = phone_clean

    @property
    def phonenumber(self):
        return self.phone.phone

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def notify(self, message, **kwargs):
        kwargs.setdefault('sound', 'default')

        self.tokens.all().send_message(
            message,
            **kwargs
        )

    @staticmethod
    def register(phone):
        try:
            user = User.objects.get(
                phone__phone=phone
            )

            if not user.enabled:
                raise UserDisabled()

            if not settings.DEBUG:
                try:
                    user.phone.send_pin()
                except PinTimeout:
                    pass
            else:
                user.phone.new_pin()

            if user.name:
                return Response(
                    status=status.HTTP_200_OK
                )
            return Response(
                status=status.HTTP_201_CREATED
            )
        except User.DoesNotExist:
            if not settings.DEBUG:
                phone, created = Phone.register(
                    phone=phone
                )
            else:
                phone = Phone.objects.create(
                    phone=phone
                )
            User.objects.create(
                phone=phone
            )

            return Response(
                status=status.HTTP_201_CREATED
            )

    @staticmethod
    def login(phone, pin, name, token):
        try:
            user = User.objects.get(
                phone__phone=phone
            )
        except User.DoesNotExist:
            return None

        if not user.enabled:
            raise UserDisabled()

        if name:
            user.name = name
        elif not user.name:
            raise BadRequest()

        if name:
            user.name = name
            user.save()

        if settings.DEBUG or user.phone.is_valid(pin=pin):
            return user


class Address(AbstractAddress):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )

    deleted = models.BooleanField(
        default=False,
        verbose_name=_('verwijderd'),
        help_text=_(
            'Duid aan of het item wacht om verwijderd te worden. Het wordt '
            'pas verwijderd wanneer er geen actieve bestellingen meer zijn '
            'met dit adres.'
        )
    )

    class Meta:
        verbose_name = _('adres')
        verbose_name_plural = _('adressen')

    def delete(self, *args, **kwargs):
        active_orders = self.order_set.filter(
            status__in=ORDER_STATUSES_ACTIVE
        ).exists()

        if active_orders:
            self.deleted = True
            self.save()
        else:
            super(Address, self).delete(*args, **kwargs)


class PaymentLink(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    redirectflow = models.ForeignKey(
        RedirectFlow,
        on_delete=models.CASCADE,
        verbose_name=_('doorverwijzing'),
        help_text=_(
            'GoCardless doorverwijzing voor het tekenen van een mandaat.'
        )
    )

    class Meta:
        unique_together = ('user', 'store',)
        verbose_name = _('betalingskoppeling')
        verbose_name_plural = _('betalingskoppelingen')

    @classmethod
    def create(cls, user, store, instance=None, **kwargs):
        if not store.staff.is_merchant:
            raise OnlinePaymentDisabled()

        if instance is None:
            cls.objects.filter(
                user=user,
                store=store
            ).delete()
        elif isinstance(instance, cls):
            instance.delete()

        merchant = store.staff.merchant

        redirectflow = RedirectFlow.create(
            description=_('Lunchbreak'),
            merchant=merchant,
            **kwargs
        )

        return cls.objects.create(
            user=user,
            store=store,
            redirectflow=redirectflow
        )

    @staticmethod
    def post_delete(sender, instance, using, **kwargs):
        instance.redirectflow.delete()


class Invite(models.Model, DirtyFieldsMixin):
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        verbose_name=_('groep'),
        help_text=_('Groep.')
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    invited_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='sent_invites',
        verbose_name=_('uitgenodigd door'),
        help_text=_('Gebruiker die de uitnodiging heeft verstuurd.')
    )
    membership = models.ForeignKey(
        'Membership',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('lidmaatschap'),
        help_text=_('Lidmaatschap.')
    )
    status = models.IntegerField(
        default=INVITE_STATUS_WAITING,
        choices=INVITE_STATUSES,
        verbose_name=_('status'),
        help_text=_('Status.')
    )

    class Meta:
        unique_together = ('group', 'user',)
        verbose_name = _('uitnodiging')
        verbose_name_plural = _('uitnodigingen')

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields()
        changed_invited_group = 'invited_by' in dirty_fields or 'group' in dirty_fields

        if self.pk is None or changed_invited_group:
            leadership = Membership.objects.filter(
                user=self.invited_by,
                group=self.group,
                leader=True
            )
            if not leadership.exists():
                raise NoInvitePermissions()

        if self.pk is None or 'user' in dirty_fields:
            membership = Membership.objects.filter(
                user=self.user,
                group=self.group
            )
            if membership.exists():
                raise AlreadyMembership()

        if 'status' in dirty_fields:
            status_dirty = dirty_fields['status']

            if status_dirty != INVITE_STATUS_WAITING:
                raise InvalidStatusChange()

            if self.status == INVITE_STATUS_ACCEPTED:
                self.membership = Membership.objects.create(
                    group=self.group,
                    user=self.user
                )

        super(Invite, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status != INVITE_STATUS_ACCEPTED:
            super(Invite, self).delete(*args, **kwargs)

    def __str__(self):
        return '{user} -> {group}, {status}'.format(
            user=self.user,
            group=self.group,
            status=self.get_status_display()
        )


class Group(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    billing = models.IntegerField(
        default=GROUP_BILLING_SEPARATE,
        choices=GROUP_BILLINGS,
        verbose_name=_('betalingswijze'),
        help_text=_('Wijze van betaling.')
    )
    users = models.ManyToManyField(
        User,
        through='Membership',
        through_fields=('group', 'user',),
        verbose_name=_('leden'),
        help_text=_('Leden.')
    )

    @classmethod
    def create(cls, name, user, billing=None):
        group = cls.objects.create(
            name=name
        )
        if billing is not None:
            group.billing = billing
        group.save()
        Membership.objects.create(
            user=user,
            group=group,
            leader=True
        )

        return group

    def __str__(self):
        return self.name


class Membership(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('groep'),
        help_text=_('Groep.')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )

    # TODO: Check whether it's the only leader
    # Perhaps by adding a unique_together:
    # ['group', 'leader']
    leader = models.BooleanField(
        default=False,
        verbose_name=_('leider'),
        help_text=_('Of dit de leider van de groep is.')
    )

    class Meta:
        unique_together = ['group', 'user']
        verbose_name = _('lidmaatschap')
        verbose_name_plural = _('lidmaatschappen')

    def __str__(self):
        return '{group}: {user}'.format(
            group=self.group,
            user=self.user
        )


class Heart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )
    added = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('toegevoegd'),
        help_text=_('Datum waarop deze persoon deze winkel "geheart" heeft.')
    )

    class Meta:
        unique_together = ('user', 'store',)
        verbose_name = _('hart')
        verbose_name_plural = _('hartjes')

    def __str__(self):
        return '{user}, {store}'.format(
            user=self.user,
            store=self.store
        )


class Reservation(CleanModelMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    seats = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name=_('plaatsen'),
        help_text=_('Plaatsen.')
    )
    placed = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('geplaatst'),
        help_text=_('Tijd waarop reservatie werd geplaatst.')
    )
    reservation_time = models.DateTimeField(
        verbose_name=_('tijd van reservatie'),
        help_text=_('Tijd van reservatie.')
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('commentaar'),
        help_text=_('Commentaar.')
    )

    suggestion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('suggestie'),
        help_text=_(
            'Indien de reservatie werd afgewezen wordt, kan er een andere '
            'datum worden voorgesteld.'
        )
    )
    response = models.TextField(
        blank=True,
        verbose_name=_('antwoord'),
        help_text=_('Antwoord van de winkel.')
    )

    status = models.IntegerField(
        choices=RESERVATION_STATUSES,
        default=RESERVATION_STATUS_PLACED,
        verbose_name=_('status'),
        help_text=_('Status.')
    )

    class Meta:
        verbose_name = _('reservatie')
        verbose_name_plural = _('reservaties')

    def clean_seats(self):
        if self.seats > self.store.seats_max:
            raise MaxSeatsExceeded()

    def clean_reservation_time(self):
        self.reservation_time = timezone_for_store(
            value=self.reservation_time,
            store=self.store
        )
        self.store.is_open(self.reservation_time)

    def clean_suggestion(self):
        self.reservation_time = timezone_for_store(
            value=self.reservation_time,
            store=self.store
        )

    def clean_status(self):
        if self.suggestion is not None:
            self.status = RESERVATION_STATUS_DENIED

    def save(self, *args, **kwargs):
        self.full_clean()

        super(Reservation, self).save(*args, **kwargs)


class AbstractOrder(CleanModelMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    objects = OrderManager()

    class Meta:
        abstract = True

    def __str__(self):
        return '{user} {id}'.format(
            user=self.user,
            id=self.id
        )

    @classmethod
    def is_valid(cls, orderedfood, **kwargs):
        if orderedfood is None or len(orderedfood) == 0:
            raise BadRequest('An order requires to have ordered food.')

        try:
            for f in orderedfood:
                if not isinstance(f, dict) and not isinstance(f, OrderedFood):
                    raise ValueError(
                        'Order creation requires a list of dicts or OrderedFoods.'
                    )
        except TypeError:
            raise BadRequest(
                'Given orderedfood is not iterable'
            )


class Order(AbstractOrder, DirtyFieldsMixin):
    placed = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('tijd van plaatsing'),
        help_text=_('Tijdstip waarop de bestelling werd geplaatst.')
    )
    receipt = models.DateTimeField(
        null=True,
        verbose_name=_('tijd afgave'),
        help_text=_('Tijd van afhalen of levering.')
    )
    status = models.PositiveIntegerField(
        choices=ORDER_STATUSES,
        default=ORDER_STATUS_PLACED,
        verbose_name=_('status'),
        help_text=_('Status.')
    )
    total = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        default=0,
        verbose_name=_('totale prijs'),
        help_text=_('Totale prijs.')
    )
    total_confirmed = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('totale gecorrigeerde prijs'),
        help_text=_(
            'Totale prijs na correctie van de winkel indien een afgewogen '
            'hoeveelheid licht afwijkt van de bestelde hoeveelheid.'
        )
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('commentaar'),
        help_text=_('Commentaar.')
    )
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('reservatie'),
        help_text=_(
            'Reservaties kunnen gekoppeld worden met een bestelling zodat '
            'men kan de bestelling bij de winkel kunnen opeten.'
        )
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('betaling'),
        help_text=_('Betaling.')
    )
    payment_method = models.IntegerField(
        choices=PAYMENT_METHODS,
        default=PAYMENT_METHOD_CASH,
        verbose_name=_('betalingswijze'),
        help_text=_('Betalingswijze.')
    )
    delivery_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('leveringsadres'),
        help_text=_('Leveringsadres.')
    )
    orderedfood = GenericRelation(
        'OrderedFood',
        related_query_name='placed_order',
        verbose_name=_('bestelde etenswaren'),
        help_text=_('Bestelde etenswaren.')
    )

    @property
    def paid(self):
        if self.payment_method == PAYMENT_METHOD_CASH:
            return self.status == ORDER_STATUS_COMPLETED
        else:
            return self.payment is None and \
                self.payment.status == PAYMENT_STATUS_PAID_OUT

    @property
    def payment_gocardless(self):
        return self.payment_method == PAYMENT_METHOD_GOCARDLESS

    class Meta:
        verbose_name = _('bestelling')
        verbose_name_plural = _('bestellingen')

    def save(self, *args, **kwargs):
        self.full_clean()

        self.total = 0
        orderedfood = self.orderedfood.all()
        for f in orderedfood:
            self.total += f.total

        dirty = self.is_dirty()
        dirty_status = None

        if dirty:
            dirty_fields = self.get_dirty_fields()
            dirty_status = dirty_fields.get('status', dirty_status)

            if dirty_status is not None:
                ORDER_STATUS_SIGNALS[self.status].send(
                    sender=self.__class__,
                    order=self
                )

        super(Order, self).save(*args, **kwargs)

        if dirty_status is not None and self.status in ORDER_STATUSES_ENDED:
            self.update_staged_deletion()

    def delete(self, *args, **kwargs):
        super(Order, self).delete(*args, **kwargs)
        self.update_staged_deletion()

    def update_staged_deletion(self, orderedfood=None):
        if orderedfood is None:
            orderedfood = self.orderedfood.all()

        if self.delivery_address is not None and self.delivery_address.deleted:
            self.delivery_address.delete()

        for f in orderedfood:
            try:
                if f.original.deleted:
                    f.original.delete()
            except Food.DoesNotExist:
                pass

    def clean_delivery_address(self):
        if self.delivery_address is not None:
            is_user_address = self.user.address_set.filter(
                id=self.delivery_address.id
            ).exists()

            if not is_user_address:
                raise LinkingError()

            if not self.store.delivers_to(self.delivery_address):
                raise NoDeliveryToAddress()

    def clean_receipt(self):
        # TODO: Check whether the store can accept an order if it is
        # for delivery and needs to be delivered asap (receipt=None).

        if self.receipt is None and self.delivery_address is None:
            if self.receipt is None:
                raise LunchbreakException(
                    _('Er moet een tijdstip voor het ophalen gegeven worden.')
                )
            self.receipt = timezone_for_store(
                value=self.receipt,
                store=self.store
            )
            self.store.is_open(
                self.receipt,
                now=self.placed
            )

    def clean_payment_method(self):
        if self.payment_method == PAYMENT_METHOD_GOCARDLESS:
            try:
                paymentlink = PaymentLink.objects.get(
                    user=self.user,
                    store=self.store
                )
                if not paymentlink.redirectflow.is_completed:
                    raise PaymentLinkNotConfirmed()
            except PaymentLink.DoesNotExist:
                raise NoPaymentLink()

    @classmethod
    def created(cls, sender, order, **kwargs):
        Staff.objects.filter(
            store_id=order.store_id
        ).notify(
            _('Er is een nieuwe bestelling binnengekomen!')
        )

    @classmethod
    def waiting(cls, sender, order, **kwargs):
        order.user.notify(
            'Je bestelling bij {store} ligt klaar!'.format(
                store=order.store.name
            )
        )

        if order.payment_method == PAYMENT_METHOD_GOCARDLESS:
            try:
                paymentlink = order.user.paymentlink_set.select_related(
                    'redirectflow__mandate'
                ).get(
                    store=order.store
                )

                if paymentlink.redirectflow.is_completed:
                    mandate = paymentlink.redirectflow.mandate
                    order.payment = Payment.create(
                        {
                            'amount': int(order.total * 100),
                            'currency': CURRENCY_EUR,
                            'links': {
                                'mandate': mandate
                            },
                            'description': _(
                                'Lunchbreak bestelling #%(order_id)s bij %(store)s.'
                            ) % {
                                'order_id': order.id,
                                'store': order.store.name
                            }
                        }
                    )
            except (PaymentLink.DoesNotExist, DjangoGoCardlessException):
                # TODO Send the user an email/text stating the failed transaction.
                order.payment_method = PAYMENT_METHOD_CASH

    @classmethod
    def denied(cls, sender, order, **kwargs):
        order.user.notify(
            _('Je bestelling werd spijtig genoeg geweigerd!')
        )


class TemporaryOrder(AbstractOrder):
    orderedfood = GenericRelation(
        'OrderedFood',
        related_query_name='temporary_order',
        verbose_name=_('bestelde etenswaren'),
        help_text=_('Bestelde etenswaren.')
    )

    class Meta:
        unique_together = ['user', 'store']
        verbose_name = _('tijdelijke bestelling')
        verbose_name_plural = _('tijdelijke bestellingen')

    def place(self, **kwargs):
        order = Order.objects.create_with_orderedfood(
            orderedfood=self.orderedfood.all(),
            user=self.user,
            store=self.store,
            **kwargs
        )
        self.delete()
        return order


class OrderedFood(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        verbose_name=_('ingrediënten'),
        help_text=_('Ingrediënten.')
    )
    amount = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=1,
        verbose_name=_('hoeveelheid'),
        help_text=_('Hoeveelheid.')
    )
    cost = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        verbose_name=_('kostprijs'),
        help_text=_('Kostprijs.')
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=(
            models.Q(app_label='customers', model='Order') |
            models.Q(app_label='customers', model='TemporaryOrder')
        )
    )
    object_id = models.PositiveIntegerField()
    order = GenericForeignKey(
        'content_type',
        'object_id',
    )
    original = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        verbose_name=_('origineel etenswaar'),
        help_text=_('Origineel etenswaar.')
    )
    is_original = models.BooleanField(
        default=False,
        verbose_name=_('identiek aan origineel'),
        help_text=_(
            'Bestelde etenswaren zijn identiek aan het origineel als er geen '
            'ingrediënten toegevoegd of afgetrokken werden.'
        )
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('commentaar'),
        help_text=_('Commentaar.')
    )

    objects = OrderedFoodManager()

    class Meta:
        verbose_name = _('besteld etenswaar')
        verbose_name_plural = _('bestelde etenswaren')

    @cached_property
    def ingredientgroups(self):
        return self.original.ingredientgroups

    @cached_property
    def amount_food(self):
        """Original amount of food, returns 1 if not variable, else original.amount."""
        return self.original.amount if self.original.foodtype.inputtype == INPUT_SI_SET else 1

    @property
    def total(self):
        """Calculate the total cost of the OrderedFood."""
        return Decimal(
            math.ceil(
                (self.cost * self.amount * self.amount_food) * 100
            ) / 100.0
        )

    def get_amount_display(self):
        """Get the amount formatted in a correct format."""
        if self.original.foodtype.inputtype == INPUT_SI_VARIABLE:
            if self.amount < 1:
                return '{value} g'.format(
                    value=self.amount * 1000
                )
            else:
                return '{value} kg'.format(
                    value=self.amount.normalize()
                )
        else:
            return int(self.amount)

    def get_total_display(self):
        """Get the total amount displayed in a correct format."""
        return '{:.2f}'.format(
            self.total
        ).replace('.', ',')

    def clean(self):
        if not self.original.is_valid_amount(self.amount):
            raise AmountInvalid()

        if not self.original.commentable and self.comment:
            self.comment = ''

        if isinstance(self.order, Order) and not self.original.is_orderable(self.order.receipt):
            raise MinDaysExceeded()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_cost(ingredients, food):
        """Calculate the base cost of the given ingredients and food.

        The base cost of the OrderedFood means that that is the cost for
        an OrderedFood with amount == 1.

        Args:
            ingredients (list): List of ingredient ids
            food (Food): Food to base the calculation off of, most of the time the original/closest food.

        Returns:
            Decimal: Base cost of edited food.
        """
        food_ingredient_relations = food.ingredientrelation_set.select_related(
            'ingredient__group',
        ).filter(
            selected=True
        )

        # All of the selected ingredients of a food
        food_ingredients = []
        # All of the ingredient groups of selected ingredients
        food_groups = []
        for ingredient_relation in food_ingredient_relations:
            ingredient = ingredient_relation.ingredient
            ingredient.selected = ingredient_relation.selected
            food_ingredients.append(ingredient)
            if ingredient_relation.selected and ingredient.group not in food_groups:
                food_groups.append(ingredient.group)

        groups_ordered = []
        cost = food.cost

        for ingredient in ingredients:
            if ingredient not in food_ingredients:
                if ingredient.group.calculation in [COST_GROUP_BOTH, COST_GROUP_ADDITIONS]:
                    cost += ingredient.cost
                elif ingredient.group not in food_groups:
                    cost += ingredient.group.cost
            if ingredient.group not in groups_ordered:
                groups_ordered.append(ingredient.group)

        groups_removed = []
        for ingredient in food_ingredients:
            if ingredient.selected and ingredient not in ingredients:
                if ingredient.group.calculation == COST_GROUP_BOTH:
                    cost -= ingredient.cost
                elif ingredient.group not in groups_removed:
                    groups_removed.append(ingredient.group)

        for group in groups_removed:
            if group not in groups_ordered:
                cost -= group.cost

        return cost

    @staticmethod
    def check_total(base_cost, food, amount, given_total):
        """Check if the given cost is correct based on a base cost, food and amount.

        Args:
            base_cost (Decimal): Base cost of edited food.
            food (Food): Original/closest food.
            amount (Decimal): Amount of food.
            given_total (Decimal): Cost given by user.

        Raises:
            CostCheckFailed: Cost given by user was calculated incorrectly.
        """
        calculated_cost = math.ceil(
            (
                base_cost * amount * (
                    # See OrderedFood.amount_food
                    food.amount
                    if food.foodtype.inputtype == INPUT_SI_SET
                    else 1
                )
            ) * 100
        ) / 100.0
        if calculated_cost != float(given_total):
            raise CostCheckFailed(
                '{calculated_cost} != {given_total}'.format(
                    calculated_cost=calculated_cost,
                    given_total=given_total
                )
            )

    def __str__(self):
        return str(self.original)


class UserToken(BaseToken):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )

    class Meta:
        verbose_name = _('gebruikerstoken')
        verbose_name_plural = _('gebruikerstokens')

    @staticmethod
    def response(user, device, service=SERVICE_INACTIVE, registration_id=''):
        from .serializers import UserTokenDetailSerializer

        token, created = UserToken.objects.create_token(
            arguments={
                'user': user,
                'device': device
            },
            defaults={
                'registration_id': registration_id,
                'service': service
            },
            clone=True
        )
        serializer = UserTokenDetailSerializer(token)
        return Response(
            serializer.data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        )


post_delete.connect(
    PaymentLink.post_delete,
    sender=PaymentLink,
    weak=False
)
