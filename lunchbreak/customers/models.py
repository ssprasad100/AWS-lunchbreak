import math

from business.models import StaffToken
from dirtyfields import DirtyFieldsMixin
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django_gocardless.config import CURRENCY_EUR
from django_gocardless.models import Payment, RedirectFlow
from lunch.config import COST_GROUP_ADDITIONS, COST_GROUP_BOTH, INPUT_SI_SET
from lunch.exceptions import BadRequest, LinkingError, NoDeliveryToAddress
from lunch.models import (AbstractAddress, BaseToken, Food, Ingredient,
                          IngredientGroup, Store)
from lunch.responses import DoesNotExist
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .config import (GROUP_BILLING_SEPARATE, GROUP_BILLINGS,
                     INVITE_STATUS_ACCEPTED, INVITE_STATUS_WAITING,
                     INVITE_STATUSES, ORDER_STATUS_PLACED,
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


class User(models.Model):
    phone = PhoneNumberField()
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

    def __str__(self):
        return '{name} {phone}'.format(
            name=self.name,
            phone=self.phone
        )

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
                return UserDisabled().response

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

            if not user.enabled:
                return UserDisabled().response

            if name:
                user.name = name
            elif not user.name:
                return BadRequest().response

            digits = Digits()
            # User just got registered in the Digits database
            if not user.request_id and not user.digits_id:
                user.digits_id = digits.register_confirm(phone, pin)['id']
            else:
                digits.signing_confirm(user.request_id, user.digits_id, pin)

            if not user.confirmed_at:
                user.confirmed_at = timezone.now()

            user.save()
            return UserToken.response(
                user=user,
                device=token['device'],
                service=token.get('service', SERVICE_INACTIVE),
                registration_id=token.get('registration_id', '')
            )
        except User.DoesNotExist:
            return DoesNotExist()


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
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    leader = models.BooleanField(
        default=False
    )

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


class Order(models.Model, DirtyFieldsMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE
    )
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
        orderedfood = self.orderedfood_set.all()
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

        super(Order, self).save(*args, **kwargs)

        if dirty_status is not None and self.status in ORDER_STATUSES_ENDED:
            self.update_staged_deletion()

    @classmethod
    def create(cls, orderedfood, **kwargs):
        if orderedfood is None or len(orderedfood) == 0:
            raise BadRequest('An order requires to have ordered food.')

        instance = cls.objects.create(**kwargs)

        try:
            for f in orderedfood:
                if isinstance(f, dict):
                    OrderedFood.objects.create(
                        order=instance,
                        **f
                    )
                elif isinstance(f, OrderedFood):
                    f.order = instance
                    f.save()
                else:
                    raise NotImplementedError(
                        'Order.create requires a dict or list of OrderedFood.'
                    )
        except:
            instance.delete()
            raise

        instance.save()
        return instance

    def delete(self, *args, **kwargs):
        super(Order, self).delete(*args, **kwargs)
        self.update_staged_deletion()

    def update_staged_deletion(self, orderedfood=None):
        if orderedfood is None:
            orderedfood = self.orderedfood_set.all()

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
        elif self.receipt is None:
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

    def __str__(self):
        return '{user} {id}'.format(
            user=self.user,
            id=self.id
        )


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
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
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

    class Meta:
        verbose_name_plural = 'Ordered food'

    @cached_property
    def ingredientgroups(self):
        return self.original.ingredientgroups

    @cached_property
    def amount_food(self):
        return self.original.amount if self.original.foodtype.inputtype == INPUT_SI_SET else 1

    @cached_property
    def total(self):
        return math.ceil(
            (self.cost * self.amount * self.amount_food) * 100
        ) / 100.0

    @staticmethod
    def check_cost(cost_calculated, food, amount, cost_given):
        if math.ceil(
                (
                    cost_calculated * amount * (
                        food.amount
                        if food.foodtype.inputtype == INPUT_SI_SET
                        else 1
                    )
                ) * 100) / 100.0 != float(cost_given):
            raise CostCheckFailed()

    def clean(self):
        if not self.original.is_valid_amount(self.amount):
            raise AmountInvalid()

        if not self.original.is_orderable(self.order.receipt):
            raise MinDaysExceeded()

        if not self.original.commentable and self.comment:
            self.comment = ''

    def save(self, ingredients=None, *args, **kwargs):
        self.full_clean()

        if self.pk is None:
            self.create(ingredients, *args, **kwargs)

        super(OrderedFood, self).save(*args, **kwargs)

    def create(self, ingredients=None, *args, **kwargs):
        if ingredients is not None:
            super(OrderedFood, self).save(*args, **kwargs)

            closest = Food.objects.closest(ingredients, self.original)
            self.check_amount(closest, self.amount)
            IngredientGroup.check_ingredients(ingredients, closest)
            cost_calculated = OrderedFood.calculate_cost(ingredients, closest)
            self.check_cost(cost_calculated, closest, self.amount, self.cost)

            self.cost = cost_calculated
            self.ingredients = ingredients
        else:
            self.check_cost(self.original.cost, self.original, self.amount, self.cost)
            self.cost = self.original.cost
            self.is_original = True

    @staticmethod
    def calculate_cost(ordered_ingredients, food):
        food_ingredient_relations = food.ingredientrelation_set.select_related(
            'ingredient__group'
        ).all()

        food_ingredients = []
        foodGroups = []
        for ingredient_relation in food_ingredient_relations:
            ingredient = ingredient_relation.ingredient
            food_ingredients.append(ingredient)
            if ingredient_relation.selected and ingredient.group not in foodGroups:
                foodGroups.append(ingredient.group)

        groups_ordered = []
        cost = food.cost

        for ingredient in ordered_ingredients:
            if ingredient not in food_ingredients:
                if ingredient.group.calculation in [COST_GROUP_BOTH, COST_GROUP_ADDITIONS]:
                    cost += ingredient.cost
                elif ingredient.group not in foodGroups:
                    cost += ingredient.group.cost
            if ingredient.group not in groups_ordered:
                groups_ordered.append(ingredient.group)

        groups_removed = []
        for ingredient in food_ingredients:
            if ingredient not in ordered_ingredients:
                if ingredient.group.calculation == COST_GROUP_BOTH:
                    cost -= ingredient.cost
                elif ingredient.group not in groups_removed:
                    groups_removed.append(ingredient.group)

        for group in groups_removed:
            if group not in groups_ordered:
                cost -= group.cost

        return cost

    def __str__(self):
        return str(self.original)


class UserToken(BaseToken):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    @staticmethod
    def response(user, device, service=SERVICE_INACTIVE, registration_id=''):
        from .serializers import UserTokenSerializer

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
        serializer = UserTokenSerializer(token)
        return Response(
            serializer.data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        )
