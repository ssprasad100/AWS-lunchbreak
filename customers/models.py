from django.db import models
from django.utils.functional import cached_property
from lunch.models import BaseToken, Food, Ingredient, Store
from phonenumber_field.modelfields import PhoneNumberField

ORDER_STATUS_PLACED = 0
ORDER_STATUS_DENIED = 1
ORDER_STATUS_RECEIVED = 2
ORDER_STATUS_STARTED = 3
ORDER_STATUS_WAITING = 4
ORDER_STATUS_COMPLETED = 5

ORDER_STATUS = (
    (ORDER_STATUS_PLACED, 'Placed'),
    (ORDER_STATUS_DENIED, 'Denied'),
    (ORDER_STATUS_RECEIVED, 'Received'),
    (ORDER_STATUS_STARTED, 'Started'),
    (ORDER_STATUS_WAITING, 'Waiting'),
    (ORDER_STATUS_COMPLETED, 'Completed')
)


class User(models.Model):
    phone = PhoneNumberField()
    name = models.CharField(max_length=128, blank=True)
    digitsId = models.CharField(unique=True, max_length=10, blank=True, null=True, verbose_name='Digits ID')
    requestId = models.CharField(max_length=32, blank=True, null=True, verbose_name='Digits Request ID')

    confirmedAt = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.name if self.name else unicode(self.phone)


class Order(models.Model):
    user = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    orderedTime = models.DateTimeField(auto_now_add=True, verbose_name='Time of order')
    pickupTime = models.DateTimeField(verbose_name='Time of pickup')
    status = models.PositiveIntegerField(choices=ORDER_STATUS, default=0)
    paid = models.BooleanField(default=False)
    total = models.DecimalField(decimal_places=2, max_digits=5, default=0)

    def save(self, *args, **kwargs):
        self.total = 0
        for f in self.orderedfood_set.all():
            self.total += f.cost * f.amount
        super(Order, self).save(*args, **kwargs)


class OrderedFood(models.Model):
    ingredients = models.ManyToManyField(Ingredient, null=True, blank=True)
    amount = models.DecimalField(decimal_places=3, max_digits=13, default=1)
    cost = models.DecimalField(decimal_places=2, max_digits=5)
    order = models.ForeignKey(Order)
    original = models.ForeignKey(Food)
    useOriginal = models.BooleanField(default=False)

    @cached_property
    def ingredientGroups(self):
        result = []
        if self.ingredients is not None:
            for ingredient in self.ingredients.all():
                if ingredient.group not in result:
                    result.append(ingredient.group)
            else:
                result = self.original.ingredientGroups
        return result

    @staticmethod
    def calculateCost(orderedIngredients, food):
        foodIngredients = food.ingredients.all()
        foodGroups = food.ingredientGroups
        orderedGroups = []
        cost = food.cost
        for ingredient in orderedIngredients:
            if ingredient not in foodIngredients:
                if ingredient.group.cost < 0:
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
