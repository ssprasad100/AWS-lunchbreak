from __future__ import unicode_literals

import math

from customers.config import (ORDER_ENDED, ORDER_STATUS,
                              ORDER_STATUS_COMPLETED, ORDER_STATUS_WAITING)
from customers.digits import Digits
from customers.exceptions import DigitsException, UserNameEmpty
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from lunch.config import COST_GROUP_ADDITIONS
from lunch.models import BaseToken, Food, Ingredient, Store, tokenGenerator
from lunch.responses import DoesNotExist
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import SERVICE_INACTIVE, DeviceManager
from rest_framework import status
from rest_framework.response import Response


class User(models.Model):
    phone = PhoneNumberField()
    name = models.CharField(max_length=255, blank=True)
    digitsId = models.CharField(unique=True, max_length=10, blank=True, null=True, verbose_name='Digits ID')
    requestId = models.CharField(max_length=32, blank=True, null=True, verbose_name='Digits Request ID')

    confirmedAt = models.DateField(blank=True, null=True)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return '{name} {phone}'.format(
            name=self.name,
            phone=self.phone
        )

    @staticmethod
    def digitsRegister(digits, phone):
        try:
            digits.register(phone)
            return True
        except DigitsException:
            return User.signIn(digits, phone)

    @staticmethod
    def digitsLogin(digits, phone):
        content = digits.signin(phone)
        return {
            'digitsId': content['login_verification_user_id'],
            'requestId': content['login_verification_request_id']
        }

    @staticmethod
    def register(phone):
        digits = Digits()
        try:
            user = User.objects.get(phone=phone)

            if not settings.TESTING:
                if user.confirmedAt:
                    digitsResult = User.digitsLogin(digits, phone)
                else:
                    digitsResult = User.digitsRegister(digits, phone)

                if digitsResult and type(digitsResult) is dict:
                    user.digitsId = digitsResult['digitsId']
                    user.requestId = digitsResult['requestId']
            user.save()

            if user.name:
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            if not settings.TESTING:
                digitsRegistration = User.digitsRegister(digits, phone)
                if digitsRegistration:
                    user = User(phone=phone)
                    if type(digitsRegistration) is dict:
                        user.digitsId = digitsRegistration['digitsId']
                        user.requestId = digitsRegistration['requestId']
                    user.save()
                    return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def login(phone, pin, name, token):
        try:
            user = User.objects.get(phone=phone)

            if not user.name:
                if not name:
                    return UserNameEmpty().getResponse()

            if name:
                user.name = name

            if not settings.TESTING:
                digits = Digits()
                # User just got registered in the Digits database
                if not user.requestId and not user.digitsId:
                    user.digitsId = digits.confirmRegistration(phone, pin)['id']
                else:
                    digits.confirmSignin(user.requestId, user.digitsId, pin)

            if not user.confirmedAt:
                user.confirmedAt = timezone.now()

            user.save()
            return UserToken.tokenResponse(
                user=user,
                device=token['device'],
                service=token['service'],
                registration_id=token['registration_id']
            )
        except User.DoesNotExist:
            return DoesNotExist()


class Heart(models.Model):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store',)

    def __unicode__(self):
        return '{user}, {store}'.format(
            user=self.user,
            store=self.store
        )


class Order(models.Model, DirtyFieldsMixin):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    orderedTime = models.DateTimeField(auto_now_add=True, verbose_name='Time of order')
    pickupTime = models.DateTimeField(verbose_name='Time of pickup')
    status = models.PositiveIntegerField(choices=ORDER_STATUS, default=0)
    paid = models.BooleanField(default=False)
    total = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    confirmedTotal = models.DecimalField(
        decimal_places=2,
        max_digits=7,
        default=None,
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.total = 0
        orderedFood = self.orderedfood_set.all()
        for f in orderedFood:
            self.total += f.total

        dirty = self.is_dirty()
        dirtyStatus = None

        if dirty:
            dirty_fields = self.get_dirty_fields()
            dirtyStatus = dirty_fields.get('status', dirtyStatus)

            if dirtyStatus is not None:

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

        if dirtyStatus is not None and self.status in ORDER_ENDED:
            for f in orderedFood:
                try:
                    if f.original.deleted:
                        f.original.delete()
                except Food.DoesNotExist:
                    pass

    @cached_property
    def eventualTotal(self):  # Used for older API versions towards customers
        return self.confirmedTotal if self.confirmedTotal is not None else self.total

    def __unicode__(self):
        return '{user} {id}'.format(
            user=self.user,
            id=self.id
        )


class OrderedFood(models.Model):
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    amount = models.DecimalField(decimal_places=3, max_digits=7, default=1)
    foodAmount = models.DecimalField(decimal_places=3, max_digits=7, default=1)
    cost = models.DecimalField(decimal_places=2, max_digits=7)
    order = models.ForeignKey(Order)
    original = models.ForeignKey(Food)
    useOriginal = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Ordered food'

    @cached_property
    def ingredientGroups(self):
        return self.original.ingredientGroups

    @cached_property
    def total(self):
        return math.ceil((self.cost * self.amount * self.foodAmount) * 100) / 100.0

    @staticmethod
    def calculateCost(orderedIngredients, food):
        foodIngredients = food.ingredients.all()
        foodGroups = food.ingredientGroups
        add = food.store.costCalculation == COST_GROUP_ADDITIONS if isinstance(food, Food) else False

        orderedGroups = []
        cost = food.cost
        for ingredient in orderedIngredients:
            if ingredient not in foodIngredients:
                if ingredient.group.cost < 0:
                    cost += ingredient.cost
                else:
                    if add:
                        cost += ingredient.cost
                    elif ingredient.group not in foodGroups:
                        cost += ingredient.group.cost
            if ingredient.group not in orderedGroups:
                orderedGroups.append(ingredient.group)

        removedGroups = []
        for ingredient in foodIngredients:
            if ingredient not in orderedIngredients:
                if ingredient.group.cost < 0:
                    cost -= ingredient.cost
                elif ingredient.group not in removedGroups:
                    removedGroups.append(ingredient.group)

        for group in removedGroups:
            if group not in orderedGroups:
                cost -= group.cost

        return cost

    def __unicode__(self):
        return unicode(self.original)


class UserTokenManager(DeviceManager):
    def createToken(self, user, device, service=SERVICE_INACTIVE, registration_id=''):
        # Active parameter is for backwards compatibility with the old login system.
        # Needs to be removed together with the old login system.
        token, created = self.get_or_create(
            user=user,
            device=device,
            service=service,
            registration_id=registration_id
        )

        # Refresh the identifier if a token already exists
        if not created:
            token.identifier = tokenGenerator()

        token.save()
        return (token, created,)


class UserToken(BaseToken):
    user = models.ForeignKey(User)

    objects = UserTokenManager()

    @staticmethod
    def tokenResponse(user, device, service=SERVICE_INACTIVE, registration_id=''):
        from customers.serializers import UserTokenSerializer

        token, created = UserToken.objects.createToken(
            user=user,
            device=device,
            service=service,
            registration_id=registration_id
        )
        tokenSerializer = UserTokenSerializer(token)
        return Response(
            tokenSerializer.data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        )
