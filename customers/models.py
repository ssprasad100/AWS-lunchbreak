from django.db import models

from lunch.models import Store, BaseStoreFood

from phonenumber_field.modelfields import PhoneNumberField

import random


ORDER_STATUS = (
	(0, 'Placed'),
	(1, 'Denied'),
	(2, 'Accepted'),
	(3, 'Started'),
	(4, 'Waiting'),
	(5, 'Completed')
)


class User(models.Model):
	phone = PhoneNumberField()
	name = models.CharField(max_length=128, blank=True)
	digitsId = models.CharField(unique=True, max_length=10, blank=True, null=True, verbose_name='Digits ID')
	requestId = models.CharField(max_length=32, blank=True, null=True, verbose_name='Digits Request ID')

	confirmedAt = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return self.name if self.name else unicode(self.phone)


class OrderedFood(BaseStoreFood):
	amount = models.IntegerField(default=1)

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


class Order(models.Model):
	user = models.ForeignKey(User)
	store = models.ForeignKey(Store)
	orderedTime = models.DateTimeField(auto_now_add=True, verbose_name='Time of order')
	pickupTime = models.DateTimeField(verbose_name='Time of pickup')
	status = models.PositiveIntegerField(choices=ORDER_STATUS, default=0)
	paid = models.BooleanField(default=False)
	food = models.ManyToManyField(OrderedFood)
	total = models.DecimalField(decimal_places=2, max_digits=5, default=0)

	def save(self, *args, **kwargs):
		if self.pk is None:
			super(Order, self).save(*args, **kwargs)
		else:
			self.total = 0
			for f in self.food.all():
				self.total += f.cost * f.amount
			super(Order, self).save(*args, **kwargs)


IDENTIFIER_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789'
IDENTIFIER_LENGTH = 64


def tokenGenerator():
	return ''.join(random.choice(IDENTIFIER_CHARS) for a in xrange(IDENTIFIER_LENGTH))


class Token(models.Model):
	identifier = models.CharField(max_length=IDENTIFIER_LENGTH, default=tokenGenerator)
	device = models.CharField(max_length=128)
	user = models.ForeignKey(User)

