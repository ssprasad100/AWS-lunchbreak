from __future__ import unicode_literals

import math

from business.models import StaffToken
from dirtyfields import DirtyFieldsMixin
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from lunch.config import COST_GROUP_ADDITIONS, COST_GROUP_BOTH, INPUT_SI_SET
from lunch.models import BaseToken, Food, Ingredient, Store
from lunch.responses import DoesNotExist
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import status
from rest_framework.response import Response

from .config import *  # NOQA
from .digits import Digits
from .exceptions import (AlreadyMembership, DigitsException,
                         InvalidStatusChange, MaxSeatsExceeded,
                         NoInvitePermissions, UserDisabled, UserNameEmpty)


class User(models.Model):
    phone = PhoneNumberField()
    name = models.CharField(
        max_length=255,
        blank=True
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

    def __unicode__(self):
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

            if not user.name:
                if not name:
                    return UserNameEmpty().response

            if name:
                user.name = name

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
        choices=INVITE_STATUS_CHOICES
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

    def __unicode__(self):
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
        choices=GROUP_BILLING_CHOICES
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

    def __unicode__(self):
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

    def __unicode__(self):
        return '{group}: {user}'.format(
            group=self.group,
            user=self.user
        )


class Heart(models.Model):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    added = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'store',)

    def __unicode__(self):
        return '{user}, {store}'.format(
            user=self.user,
            store=self.store
        )


class Reservation(models.Model):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)

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
        choices=RESERVATION_STATUS,
        default=RESERVATION_STATUS_PLACED
    )

    def clean(self, *args, **kwargs):
        if self.seats > self.store.seats_max:
            raise MaxSeatsExceeded()

        Store.is_open(self.store, self.reservation_time)

        super(Reservation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.suggestion is not None:
            self.status = RESERVATION_STATUS_DENIED

        super(Reservation, self).save(*args, **kwargs)


class Order(models.Model, DirtyFieldsMixin):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    placed = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Time of placement'
    )
    pickup = models.DateTimeField(
        verbose_name='Time of pickup'
    )
    status = models.PositiveIntegerField(
        choices=ORDER_STATUS,
        default=ORDER_STATUS_PLACED
    )
    paid = models.BooleanField(
        default=False
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
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        self.total = 0
        orderedfood = self.orderedfood_set.all()
        for f in orderedfood:
            self.total += f.total

        if self.pk is None:
            StaffToken.objects.filter(
                staff__store_id=self.store_id
            ).send_message(
                'Er is een nieuwe bestelling binnengekomen!',
                sound='default'
            )

        dirty = self.is_dirty()
        dirty_status = None

        if dirty:
            dirty_fields = self.get_dirty_fields()
            dirty_status = dirty_fields.get('status', dirty_status)

            if dirty_status is not None:
                if self.status == ORDER_STATUS_WAITING:
                    self.user.usertoken_set.all().send_message(
                        'Je bestelling bij {store} ligt klaar!'.format(
                            store=self.store.name
                        ),
                        sound='default'
                    )

                if self.status == ORDER_STATUS_COMPLETED:
                    self.paid = True

        super(Order, self).save(*args, **kwargs)

        if dirty_status is not None and self.status in ORDER_ENDED:
            for f in orderedfood:
                try:
                    if f.original.deleted:
                        f.original.delete()
                except Food.DoesNotExist:
                    pass

    def __unicode__(self):
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
    order = models.ForeignKey(Order)
    original = models.ForeignKey(Food)
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

    def __unicode__(self):
        return unicode(self.original)


class UserToken(BaseToken):
    user = models.ForeignKey(User)

    @staticmethod
    def response(user, device, service=SERVICE_INACTIVE, registration_id=''):
        from customers.serializers import UserTokenSerializer

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
