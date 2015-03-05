from django.db import models
from lunch.models import BaseStoreFood, Store, BaseToken
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
        for f in self.food.all():
            self.total += f.cost * f.amount
        super(Order, self).save(*args, **kwargs)


class OrderedFood(BaseStoreFood):
    amount = models.IntegerField(default=1)
    order = models.ForeignKey(Order, related_name='food')

    @staticmethod
    def calculateCost(orderedIngredients, food):
        foodIngredients = food.ingredients.all()
        cost = food.cost
        for ingredient in orderedIngredients:
            if ingredient not in foodIngredients:
                cost += ingredient.cost
        for ingredient in foodIngredients:
            if ingredient not in orderedIngredients:
                cost -= ingredient.cost
        return cost


class UserToken(BaseToken):
    user = models.ForeignKey(User)
