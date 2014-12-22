from django.db import models
from django.utils.functional import cached_property

from lunch.exceptions import AddressNotFound

import requests
import random

IDENTIFIER_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789'
IDENTIFIER_LENGTH = 64


class LunchbreakManager(models.Manager):

	def nearby(self, latitude, longitude, proximity):
		# Haversine formule is het beste om te gebruiken bij korte afstanden.
		# d = 2 * r * asin( sqrt( sin^2( ( lat2-lat1 ) / 2 ) + cos(lat1)*cos(lat2)*sin^2( (lon2-lon1) / 2 ) ) )
		haversine = '''
		(
			(2*6371)
			* ASIN(
				SQRT(
					POW(
						SIN( (RADIANS(%s) - RADIANS(latitude)) / 2 )
					, 2)
					+ (
						COS(RADIANS(latitude))
						* COS(RADIANS(%s))
						* POW(
							SIN(
								(RADIANS(%s) - RADIANS(longitude)) / 2
							)
						, 2
						)
					)
				)
			)
		)
		'''
		haversine_where = "{} < %s".format(haversine)
		return self.get_queryset()\
			.exclude(latitude=None)\
			.exclude(longitude=None)\
			.extra(
				select={'distance': haversine},
				select_params=[latitude, latitude, longitude],
				where=[haversine_where],
				params=[latitude, latitude, longitude, proximity],
				order_by=['distance']
			)


class Icon(models.Model):
	iconId = models.IntegerField(primary_key=True)
	description = models.CharField(max_length=64, blank=True)

	def __unicode__(self):
		return str(self.iconId) + '. ' + self.description


class StoreCategory(models.Model):
	name = models.CharField(max_length=64)

	class Meta:
		verbose_name_plural = 'Store categories'

	def __unicode__(self):
		return self.name


class Store(models.Model):
	name = models.CharField(max_length=256)

	country = models.CharField(max_length=256)
	province = models.CharField(max_length=256)
	city = models.CharField(max_length=256)
	code = models.CharField(max_length=20, verbose_name="Postal code")
	street = models.CharField(max_length=256)
	number = models.IntegerField()

	objects = LunchbreakManager()
	latitude = models.DecimalField(blank=True, decimal_places=7, max_digits=10)
	longitude = models.DecimalField(blank=True, decimal_places=7, max_digits=10)

	categories = models.ManyToManyField(StoreCategory)

	GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
	GEOCODING_KEY = 'AIzaSyD7jRgPzUxQ4fdghdwoyTnD5hB6EOtpDhE'
	ADDRESS_FORMAT = '%s,+%s,+%s+%s,+%s+%s'

	def save(self, *args, **kwargs):
		address = self.ADDRESS_FORMAT % (self.country, self.province, self.street, self.number, self.code, self.city,)
		response = requests.get(self.GEOCODING_URL, params={'address': address, 'key': self.GEOCODING_KEY})
		result = response.json()

		if not result['results']:
			raise AddressNotFound

		self.latitude = result['results'][0]['geometry']['location']['lat']
		self.longitude = result['results'][0]['geometry']['location']['lng']

		super(Store, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name + ', ' + self.city


class IngredientGroup(models.Model):
	name = models.CharField(max_length=256)
	maximum = models.IntegerField(default=0, verbose_name='Maximum amount')

	@cached_property
	def ingredients(self):
		return self.ingredient_set.all()

	def __unicode__(self):
		return self.name


class BaseIngredient(models.Model):
	name = models.CharField(max_length=256)
	cost = models.DecimalField(decimal_places=2, max_digits=5, default=0)
	group = models.ForeignKey(IngredientGroup)
	icon = models.ForeignKey(Icon, null=True)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.name + ' (' + unicode(self.group) + ')'


class DefaultIngredient(BaseIngredient):
	pass


class Ingredient(BaseIngredient):
	store = models.ForeignKey(Store)


class BaseFoodCategory(models.Model):
	name = models.CharField(max_length=128)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.name


class DefaultFoodCategory(BaseFoodCategory):

	class Meta:
		verbose_name_plural = 'Default food categories'


class FoodCategory(BaseFoodCategory):
	store = models.ForeignKey(Store)

	class Meta:
		verbose_name_plural = 'Food categories'


class User(models.Model):
	# Maximum european length (with +) is +XXX and 13 numbers -> 17
	phone = models.CharField(max_length=17, primary_key=True)
	name = models.CharField(max_length=128, blank=True)
	userId = models.CharField(max_length=10, blank=True, null=True, verbose_name='User ID')
	requestId = models.CharField(max_length=32, blank=True, null=True, verbose_name='Request ID')

	confirmedAt = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return self.name if self.name else self.phone


class BaseFood(models.Model):
	name = models.CharField(max_length=256)
	cost = models.DecimalField(decimal_places=2, max_digits=5)
	icon = models.ForeignKey(Icon, null=True, blank=True)

	class Meta:
		abstract = True

	@cached_property
	def ingredientGroups(self):
		result = []
		for ingredient in self.ingredients.all():
			if ingredient.group not in result:
				result.append(ingredient.group)
		return result

	def __unicode__(self):
		return self.name


class DefaultFood(BaseFood):
	category = models.ForeignKey(DefaultFoodCategory, null=True, blank=True)
	ingredients = models.ManyToManyField(DefaultIngredient, null=True, blank=True)


class Food(BaseFood):
	category = models.ForeignKey(FoodCategory, null=True, blank=True)
	ingredients = models.ManyToManyField(Ingredient, null=True, blank=True)
	store = models.ForeignKey(Store)


class OrderedFood(BaseFood):
	category = models.ForeignKey(FoodCategory, null=True, blank=True)
	ingredients = models.ManyToManyField(Ingredient, null=True, blank=True)
	store = models.ForeignKey(Store)


STATUS_CHOICES = (
	(0, 'Placed'),
	(1, 'Denied'),
	(2, 'Accepted'),
	(3, 'Started'),
	(4, 'Waiting'),
	(5, 'Completed')
)


class Order(models.Model):
	user = models.ForeignKey(User)
	store = models.ForeignKey(Store)
	orderedTime = models.DateTimeField(auto_now_add=True, verbose_name='Time of order')
	pickupTime = models.DateTimeField(verbose_name='Time of pickup')
	status = models.IntegerField(choices=STATUS_CHOICES, default=0)
	paid = models.BooleanField(default=False)
	food = models.ManyToManyField(OrderedFood)


def tokenGenerator():
	return ''.join(random.choice(IDENTIFIER_CHARS) for a in xrange(IDENTIFIER_LENGTH))


class Token(models.Model):
	identifier = models.CharField(max_length=IDENTIFIER_LENGTH, default=tokenGenerator)
	device = models.CharField(max_length=128)
	user = models.ForeignKey(User, db_column='phone')
