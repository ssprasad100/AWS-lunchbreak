from django.db import models
from django.utils.functional import cached_property
from django.db.models import Count

from phonenumber_field.modelfields import PhoneNumberField

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

	def closestFood(self, orderedFood=False, ingredients=None, storeId=None):
		ingredients = ingredients if ingredients else orderedFood.ingredients.all()
		storeId = storeId if storeId else orderedFood.store_id

		food = Food.objects.annotate(count=Count('ingredients')).filter(count=len(ingredients)).filter(store_id=storeId)
		ids = orderedFood.ingredients.values_list('id', flat=True) if orderedFood and ingredients is None else ingredients
		for _id in ids:
			food = food.filter(ingredients__id=_id)
		if(len(food) > 0):
			return (True, food[0],)
		else:
			if ingredients is None:
				return (False, Food.objects.raw('''
				SELECT
					lunch_food.id,
					lunch_food.name,
					lunch_food.cost,
					SUM(lunch_ingredient.cost) AS difference
				FROM `lunch_food`
					INNER JOIN `lunch_food_ingredients` ON lunch_food.id = lunch_food_ingredients.food_id
					INNER JOIN `lunch_ingredient` ON lunch_food_ingredients.ingredient_id = lunch_ingredient.id
				WHERE lunch_ingredient.id NOT IN (
					SELECT
						lunch_food_ingredients.ingredient_id
					FROM `lunch_food`
						INNER JOIN `lunch_food_ingredients` ON lunch_food.id = lunch_food_ingredients.food_id
						LEFT JOIN `lunch_orderedfood_ingredients` ON lunch_food_ingredients.ingredient_id = lunch_orderedfood_ingredients.ingredient_id
						INNER JOIN `lunch_orderedfood` ON lunch_orderedfood_ingredients.orderedfood_id = lunch_orderedfood.id
					WHERE lunch_orderedfood.id = %s AND lunch_orderedfood.store_id = %s
				)
				GROUP BY lunch_food.id
				ORDER BY difference ASC, cost DESC;
				''', [orderedFood.id, orderedFood.store_id])[0],)
			else:
				#
				return (False, Food.objects.raw('''
				SELECT
					lunch_food.id,
					lunch_food.name,
					lunch_food.cost,
					SUM(lunch_ingredient.cost) AS difference
				FROM `lunch_food`
					INNER JOIN `lunch_food_ingredients` ON lunch_food.id = lunch_food_ingredients.food_id
					INNER JOIN `lunch_ingredient` ON lunch_food_ingredients.ingredient_id = lunch_ingredient.id
				WHERE lunch_ingredient.id NOT IN (
					''' + ','.join([str(i) for i in ingredients]) + '''
				)
				GROUP BY lunch_food.id
				ORDER BY difference ASC, cost DESC;
				''')[0],)


ICONS = (
	(0, 'Icoontje 0'),
	(1, 'Icoontje 1'),
	(2, 'Icoontje 2'),
	(3, 'Icoontje 3'),
	(4, 'Icoontje 4'),
	(5, 'Icoontje 5')
)


STATUS_CHOICES = (
	(0, 'Placed'),
	(1, 'Denied'),
	(2, 'Accepted'),
	(3, 'Started'),
	(4, 'Waiting'),
	(5, 'Completed')
)


DAYS = (
	(0, 'Maandag'),
	(1, 'Dinsdag'),
	(2, 'Woensdag'),
	(3, 'Donderdeg'),
	(4, 'Vrijdag'),
	(5, 'Zaterdag'),
	(6, 'Zondag')
)


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
	code = models.CharField(max_length=20, verbose_name='Postal code')
	street = models.CharField(max_length=256)
	number = models.PositiveIntegerField()

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


class OpeningHours(models.Model):
	store = models.ForeignKey(Store)
	day = models.IntegerField(choices=DAYS)

	opening = models.TimeField()
	closing = models.TimeField()

	class Meta:
		verbose_name_plural = 'Opening hours'

	def __unicode__(self):
		return '%s. %s - %s' % (self.day, self.opening, self.closing,)


class HolidayPeriod(models.Model):
	store = models.ForeignKey(Store)
	description = models.CharField(max_length=128)

	start = models.DateTimeField()
	end = models.DateTimeField()

	closed = models.BooleanField(default=True)


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
	icon = models.IntegerField(choices=ICONS, default=0)

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
	priority = models.PositiveIntegerField(default=0)

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
	phone = PhoneNumberField()
	name = models.CharField(max_length=128, blank=True)
	digitsId = models.CharField(unique=True, max_length=10, blank=True, null=True, verbose_name='Digits ID')
	requestId = models.CharField(max_length=32, blank=True, null=True, verbose_name='Digits Request ID')

	confirmedAt = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return self.name if self.name else unicode(self.phone)


class FoodType(models.Model):
	name = models.CharField(max_length=64)
	icon = models.IntegerField(choices=ICONS, default=0)

	def __unicode__(self):
		return self.name


class BaseFood(models.Model):
	name = models.CharField(max_length=256)
	cost = models.DecimalField(decimal_places=2, max_digits=5)
	foodType = models.ForeignKey(FoodType, null=True)

	objects = LunchbreakManager()

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


class BaseStoreFood(BaseFood):
	category = models.ForeignKey(FoodCategory, null=True, blank=True)
	ingredients = models.ManyToManyField(Ingredient, null=True, blank=True)
	store = models.ForeignKey(Store)

	class Meta:
		abstract = True


class Food(BaseStoreFood):
	pass


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
	status = models.IntegerField(choices=STATUS_CHOICES, default=0)
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


def tokenGenerator():
	return ''.join(random.choice(IDENTIFIER_CHARS) for a in xrange(IDENTIFIER_LENGTH))


class Token(models.Model):
	identifier = models.CharField(max_length=IDENTIFIER_LENGTH, default=tokenGenerator)
	device = models.CharField(max_length=128)
	user = models.ForeignKey(User)
