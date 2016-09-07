import math

from business.models import StaffToken
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django_gocardless.config import CURRENCY_EUR
from django_gocardless.models import Payment, RedirectFlow
from lunch.config import (COST_GROUP_ADDITIONS, COST_GROUP_BOTH, INPUT_SI_SET,
                          INPUT_SI_VARIABLE)
from lunch.exceptions import BadRequest, LinkingError, NoDeliveryToAddress
from lunch.models import AbstractAddress, BaseToken, Food, Ingredient, Store
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .config import (GROUP_BILLING_SEPARATE, GROUP_BILLINGS,
                     INVITE_STATUS_ACCEPTED, INVITE_STATUS_WAITING,
                     INVITE_STATUSES, ORDER_STATUS_DENIED, ORDER_STATUS_PLACED,
                     ORDER_STATUS_WAITING, ORDER_STATUSES,
                     ORDER_STATUSES_ACTIVE, ORDER_STATUSES_ENDED,
                     PAYMENT_METHOD_CASH, PAYMENT_METHOD_GOCARDLESS,
                     PAYMENT_METHODS, RESERVATION_STATUS_DENIED,
                     RESERVATION_STATUS_PLACED, RESERVATION_STATUSES)
from .digits import Digits
from .exceptions import (AlreadyMembership, AmountInvalid, CostCheckFailed,
                         DigitsException, InvalidStatusChange,
                         MaxSeatsExceeded, MinDaysExceeded,
                         NoInvitePermissions, NoPaymentLink,
                         OnlinePaymentDisabled, PaymentLinkNotConfirmed,
                         UserDisabled)
from .managers import OrderedFoodManager, OrderManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(
        unique=True
    )
    name = models.CharField(
        max_length=255
    )
    digits_id = models.CharField(
        unique=True,
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Digits ID'
    )
    request_id = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Digits Request ID'
    )

    confirmed_at = models.DateField(
        blank=True,
        null=True
    )
    enabled = models.BooleanField(
        default=True
    )

    paymentlinks = models.ManyToManyField(
        Store,
        through='PaymentLink',
        through_fields=(
            'user',
            'store',
        ),
        blank=True
    )
    is_staff = models.BooleanField(
        default=False
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = [
        'name',
    ]

    objects = UserManager()

    def __str__(self):
        return '{name} {phone}'.format(
            name=self.name,
            phone=self.phone
        )

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    @classmethod
    def digits_register(cls, digits, phone):
        try:
            digits.register(phone)
            return True
        except DigitsException:
            return cls.digits_login(digits, phone)

    @staticmethod
    def digits_login(digits, phone):
        content = digits.signin(phone)
        return {
            'digits_id': content['login_verification_user_id'],
            'request_id': content['login_verification_request_id']
        }

    @staticmethod
    def register(phone):
        digits = Digits()
        try:
            user = User.objects.get(phone=phone)

            if not user.enabled:
                return UserDisabled().responsese

            if not settings.DEBUG:
                if user.confirmed_at:
                    digits_result = User.digits_login(digits, phone)
                else:
                    digits_result = User.digits_register(digits, phone)

                if digits_result and type(digits_result) is dict:
                    user.digits_id = digits_result['digits_id']
                    user.request_id = digits_result['request_id']
                user.save()

            if user.name:
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            digits_registration = User.digits_register(digits, phone)
            if digits_registration:
                user = User(phone=phone)
                if type(digits_registration) is dict:
                    user.digits_id = digits_registration['digits_id']
                    user.request_id = digits_registration['request_id']
                user.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def login(phone, pin, name, token):
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        if not user.enabled:
            raise UserDisabled()

        if name:
            user.name = name
        elif not user.name:
            raise BadRequest()

        digits = Digits()
        # User just got registered in the Digits database
        if not settings.DEBUG:
            if not user.request_id and not user.digits_id:
                user.digits_id = digits.register_confirm(phone, pin)['id']
            else:
                digits.signing_confirm(
                    user.request_id,
                    user.digits_id,
                    pin
                )

        if not user.confirmed_at:
            user.confirmed_at = timezone.now()

        user.save()
        return user


class Address(AbstractAddress):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    deleted = models.BooleanField(
        default=False
    )

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
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    redirectflow = models.ForeignKey(
        RedirectFlow,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'store',)

    @classmethod
    def create(cls, user, store, instance=None):
        if not store.staff.is_merchant:
            raise OnlinePaymentDisabled()

        if instance is not None and isinstance(instance, cls):
            instance.delete()

        merchant = store.staff.merchant

        redirectflow = RedirectFlow.create(
            description=_('Lunchbreak orders'),
            merchant=merchant
        )

        return cls.objects.create(
            user=user,
            store=store,
            redirectflow=redirectflow
        )


class Invite(models.Model, DirtyFieldsMixin):
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE
    )
    invited_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='sent_invites'
    )
    membership = models.ForeignKey(
        'Membership',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    status = models.IntegerField(
        default=INVITE_STATUS_WAITING,
        choices=INVITE_STATUSES
    )

    class Meta:
        unique_together = ('group', 'user',)

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
        max_length=255
    )
    billing = models.IntegerField(
        default=GROUP_BILLING_SEPARATE,
        choices=GROUP_BILLINGS
    )
    users = models.ManyToManyField(
        User,
        through='Membership',
        through_fields=('group', 'user',)
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
        related_name='memberships'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    # TODO: Check whether it's the only leader
    # Perhaps by adding a unique_together:
    # ['group', 'leader']
    leader = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ['group', 'user']

    def __str__(self):
        return '{group}: {user}'.format(
            group=self.group,
            user=self.user
        )


class Heart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )
    added = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'store',)

    def __str__(self):
        return '{user}, {store}'.format(
            user=self.user,
            store=self.store
        )


class Reservation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )

    seats = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1)
        ]
    )
    placed = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Time of placement'
    )
    reservation_time = models.DateTimeField(
        verbose_name='Time of reservation'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Comment from user'
    )

    suggestion = models.DateTimeField(
        null=True,
        blank=True
    )
    response = models.TextField(
        blank=True,
        verbose_name='Response from store'
    )

    status = models.IntegerField(
        choices=RESERVATION_STATUSES,
        default=RESERVATION_STATUS_PLACED
    )

    def clean(self, *args, **kwargs):
        if self.seats > self.store.seats_max:
            raise MaxSeatsExceeded()

        self.store.is_open(self.reservation_time)

        super(Reservation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.suggestion is not None:
            self.status = RESERVATION_STATUS_DENIED

        super(Reservation, self).save(*args, **kwargs)


class AbstractOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
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
        if orderedfood is None or not isinstance(orderedfood, list) or len(orderedfood) == 0:
            raise BadRequest('An order requires to have ordered food.')

        for f in orderedfood:
            if not isinstance(f, dict) and not isinstance(f, OrderedFood):
                raise ValueError(
                    'Order creation requires a list of dicts or OrderedFoods.'
                )


class Order(AbstractOrder, DirtyFieldsMixin):
    placed = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Time of placement'
    )
    receipt = models.DateTimeField(
        null=True,
        verbose_name='Time of receipt'
    )
    status = models.PositiveIntegerField(
        choices=ORDER_STATUSES,
        default=ORDER_STATUS_PLACED
    )
    total = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        default=0
    )
    total_confirmed = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        default=None,
        null=True,
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    payment_method = models.IntegerField(
        choices=PAYMENT_METHODS,
        default=PAYMENT_METHOD_CASH
    )
    delivery_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    orderedfood = GenericRelation(
        'OrderedFood',
        related_query_name='placed_order'
    )

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.pk is None:
            StaffToken.objects.filter(
                staff__store_id=self.store_id
            ).send_message(
                'Er is een nieuwe bestelling binnengekomen!',
                sound='default'
            )

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
                if self.status == ORDER_STATUS_WAITING:
                    self.waiting()
                elif self.status == ORDER_STATUS_DENIED:
                    StaffToken.objects.filter(
                        staff__store_id=self.store_id
                    ).send_message(
                        'Je bestelling is spijtig genoeg geweigerd!',
                        sound='default'
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

    def waiting(self):
        """Called when status is set to waiting.

        ..note:
            Does not save the instance.
        """
        self.user.usertoken_set.all().send_message(
            'Je bestelling bij {store} ligt klaar!'.format(
                store=self.store.name
            ),
            sound='default'
        )

        if self.payment_method == PAYMENT_METHOD_GOCARDLESS:
            try:
                paymentlink = self.user.paymentlink_set.select_related(
                    'redirectflow__mandate'
                ).get(
                    store=self.store
                )

                if paymentlink.redirectflow.is_completed:
                    mandate = paymentlink.redirectflow.mandate
                    self.payment = Payment.create(
                        {
                            'amount': int(self.total * 100),
                            'currency': CURRENCY_EUR,
                            'links': {
                                'mandate': mandate
                            },
                            'description': _(
                                'Lunchbreak bestelling #%(order_id)s bij %(store)s.'
                            ) % {
                                'order_id': self.id,
                                'store': self.store.name
                            }
                        }
                    )
            except PaymentLink.DoesNotExist:
                pass
            # TODO Send the user an email/text stating the failed transaction.
            self.payment_method = PAYMENT_METHOD_CASH

    def clean(self):
        if self.delivery_address is not None:
            is_user_address = self.user.address_set.filter(
                id=self.delivery_address.id
            ).exists()

            if not is_user_address:
                raise LinkingError()

            if not self.store.delivers_to(self.delivery_address):
                raise NoDeliveryToAddress()
        else:
            if self.receipt is None:
                raise ValidationError(
                    _('Receipt cannot be None for pickup.')
                )
            self.store.is_open(self.receipt)

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


class TemporaryOrder(AbstractOrder):
    orderedfood = GenericRelation(
        'OrderedFood',
        related_query_name='temporary_order'
    )

    class Meta:
        unique_together = ['user', 'store']


class OrderedFood(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True
    )
    amount = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=1
    )
    cost = models.DecimalField(
        decimal_places=2,
        max_digits=7
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
        'object_id'
    )
    original = models.ForeignKey(
        Food,
        on_delete=models.CASCADE
    )
    is_original = models.BooleanField(
        default=False
    )
    comment = models.TextField(
        blank=True
    )

    objects = OrderedFoodManager()

    class Meta:
        verbose_name_plural = 'Ordered food'

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
        return math.ceil(
            (self.cost * self.amount * self.amount_food) * 100
        ) / 100.0

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
        if math.ceil(
                (
                    base_cost * amount * (
                        # See OrderedFood.amount_food
                        food.amount
                        if food.foodtype.inputtype == INPUT_SI_SET
                        else 1
                    )
                ) * 100) / 100.0 != float(given_total):
            raise CostCheckFailed()

    def __str__(self):
        return str(self.original)


class UserToken(BaseToken):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

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
