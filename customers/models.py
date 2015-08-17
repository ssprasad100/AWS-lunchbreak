import math

from django.db import models
from django.utils.functional import cached_property
from lunch.config import (COST_GROUP_ADDITIONS, ORDER_ENDED, ORDER_STATUS,
                          ORDER_STATUS_COMPLETED)
from lunch.models import BaseToken, Food, Ingredient, Store
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    phone = PhoneNumberField()
    name = models.CharField(max_length=255, blank=True)
    digitsId = models.CharField(unique=True, max_length=10, blank=True, null=True, verbose_name='Digits ID')
    requestId = models.CharField(max_length=32, blank=True, null=True, verbose_name='Digits Request ID')

    confirmedAt = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.name if self.name else unicode(self.phone)


class Heart(models.Model):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store',)


class Order(models.Model):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    orderedTime = models.DateTimeField(auto_now_add=True, verbose_name='Time of order')
    pickupTime = models.DateTimeField(verbose_name='Time of pickup')
    status = models.PositiveIntegerField(choices=ORDER_STATUS, default=0)
    paid = models.BooleanField(default=False)
    total = models.DecimalField(decimal_places=2, max_digits=7, default=0)
    confirmedTotal = models.DecimalField(decimal_places=2, max_digits=7, default=None, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total = 0
        orderedFood = self.orderedfood_set.all()
        for f in orderedFood:
            self.total += f.total

        if self.status == ORDER_STATUS_COMPLETED:
            self.paid = True

        super(Order, self).save(*args, **kwargs)

        if self.status in ORDER_ENDED:
            for f in orderedFood:
                if f.original.deleted:
                    f.original.delete()

    @cached_property
    def eventualTotal(self):  # Used for older API versions towards customers
        return self.confirmedTotal if self.confirmedTotal is not None else self.total

    def __unicode__(self):
        return 'Order #' + str(self.id)


class OrderedFood(models.Model):
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    amount = models.DecimalField(decimal_places=3, max_digits=7, default=1)
    foodAmount = models.DecimalField(decimal_places=3, max_digits=7, default=1)
    cost = models.DecimalField(decimal_places=2, max_digits=7)
    order = models.ForeignKey(Order)
    original = models.ForeignKey(Food)
    useOriginal = models.BooleanField(default=False)

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


class UserToken(BaseToken):
    user = models.ForeignKey(User)
