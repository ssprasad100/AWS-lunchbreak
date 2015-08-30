from __future__ import unicode_literals

import random
from datetime import datetime, time, timedelta

import requests
from customers.config import ORDER_ENDED
from customers.exceptions import MinTimeExceeded, PastOrderDenied, StoreClosed
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from lunch.config import (COST_GROUP_ALWAYS, COST_GROUP_CALCULATIONS, DAYS,
                          ICONS, INPUT_AMOUNT, INPUT_TYPES,
                          TOKEN_IDENTIFIER_CHARS, TOKEN_IDENTIFIER_LENGTH)
from lunch.exceptions import (AddressNotFound, IngredientGroupMaxExceeded,
                              IngredientGroupsMinimumNotMet,
                              InvalidFoodTypeAmount, InvalidIngredientLinking,
                              InvalidStoreLinking)
from push_notifications.models import BareDevice


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

    def closestFood(self, ingredients, original):
        ingredientsIn = -1 if len(ingredients) == 0 else '''
            CASE WHEN lunch_ingredient.id IN (%s)
                THEN
                    1
                ELSE
                    -1
                END''' % ','.join([str(i.id) for i in ingredients])

        return Food.objects.raw(('''
            SELECT
                lunch_food.id,
                lunch_food.name,
                lunch_food.cost
            FROM
                `lunch_food`
                LEFT JOIN
                    `lunch_ingredientrelation` ON lunch_food.id = lunch_ingredientrelation.food_id AND lunch_ingredientrelation.typical = 1
                LEFT JOIN
                    `lunch_ingredient` ON lunch_ingredientrelation.ingredient_id = lunch_ingredient.id
            WHERE
                lunch_food.foodType_id = %d AND
                lunch_food.store_id = %d
            GROUP BY
                lunch_food.id
            ORDER BY
                SUM(
                    CASE WHEN lunch_ingredient.id IS NULL
                        THEN
                            0
                        ELSE
                            %s
                        END
                ) DESC,
                (lunch_food.id = %d) DESC,
                lunch_food.cost ASC;''') % (original.foodType.id, original.store.id, ingredientsIn, original.id,))[0]


class StoreCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.PositiveIntegerField(choices=ICONS, default=0)

    class Meta:
        verbose_name_plural = 'Store categories'

    def __unicode__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=255)

    objects = LunchbreakManager()

    country = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=20, verbose_name='Postal code')
    street = models.CharField(max_length=255)
    number = models.PositiveIntegerField()
    latitude = models.DecimalField(blank=True, decimal_places=7, max_digits=10)
    longitude = models.DecimalField(blank=True, decimal_places=7, max_digits=10)

    categories = models.ManyToManyField(StoreCategory)
    minTime = models.PositiveIntegerField(default=60)
    orderTime = models.TimeField(default=time(hour=12))
    hearts = models.ManyToManyField('customers.User', through='customers.Heart', blank=True)
    costCalculation = models.PositiveIntegerField(choices=COST_GROUP_CALCULATIONS, default=COST_GROUP_ALWAYS)

    lastModified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        address = '{country},+{province},+{street}+{number},+{postcode}+{city}'.format(
            country=self.country,
            province=self.province,
            street=self.street,
            number=self.number,
            postcode=self.postcode,
            city=self.city,
        )
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params={
                'address': address,
                'key': settings.GOOGLE_CLOUD_SECRET
            }
        )
        result = response.json()

        if not result['results']:
            raise AddressNotFound()

        self.latitude = result['results'][0]['geometry']['location']['lat']
        self.longitude = result['results'][0]['geometry']['location']['lng']

        super(Store, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{name}, {city}'.format(
            name=self.name,
            city=self.city
        )

    @cached_property
    def heartsCount(self):
        return self.hearts.count()

    @staticmethod
    def checkOpen(store, pickupTime, now=None):
        now = timezone.now() if now is None else now

        if pickupTime < now:
            raise PastOrderDenied()

        if pickupTime - now < timedelta(minutes=store.minTime):
            raise MinTimeExceeded()

        holidayPeriods = HolidayPeriod.objects.filter(store=store, start__lte=pickupTime, end__gte=pickupTime)

        closed = False
        for holidayPeriod in holidayPeriods:
            if not holidayPeriod.closed:
                break
            else:
                closed = True
        else:
            # Open stores are
            if closed:
                raise StoreClosed()

            # datetime.weekday(): return monday 0 - sunday 6
            # datetime.strftime('%w'): return sunday 0 - monday 6
            pickupDay = pickupTime.strftime('%w')
            openingHours = OpeningHours.objects.filter(store=store, day=pickupDay)
            pTime = pickupTime.time()

            for o in openingHours:
                if o.opening <= pTime <= o.closing:
                    break
            else:
                # If the for loop is not stopped by the break, it means that the time of pickup is never when the store is open.
                raise StoreClosed()


class OpeningHours(models.Model):
    store = models.ForeignKey(Store)
    day = models.PositiveIntegerField(choices=DAYS)

    opening = models.TimeField()
    closing = models.TimeField()

    class Meta:
        verbose_name_plural = 'Opening hours'

    def clean(self):
        if self.opening >= self.closing:
            raise ValidationError('Opening needs to be before closing.')

    def save(self, *args, **kwargs):
        self.clean()
        self.store.save()
        super(OpeningHours, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{day} {opening}-{closing}'.format(
            day=self.get_day_display(),
            opening=self.opening,
            closing=self.closing
        )


class HolidayPeriod(models.Model):
    store = models.ForeignKey(Store)
    description = models.CharField(max_length=255)

    start = models.DateTimeField()
    end = models.DateTimeField()

    closed = models.BooleanField(default=True)

    def clean(self):
        if self.start >= self.end:
            raise ValidationError('Start needs to be before end.')

    def save(self, *args, **kwargs):
        self.clean()
        self.store.save()
        super(HolidayPeriod, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{start}-{end} {state}'.format(
            start=self.start,
            end=self.end,
            state='closed' if self.closed else 'open'
        )


class FoodType(models.Model):
    name = models.CharField(max_length=255)
    icon = models.PositiveIntegerField(choices=ICONS, default=ICONS[0][0])
    quantifier = models.CharField(max_length=255, blank=True, null=True)
    inputType = models.PositiveIntegerField(choices=INPUT_TYPES, default=INPUT_TYPES[0][0])

    def isValidAmount(self, amount, quantity=None):
        return amount > 0 \
            and (self.inputType != INPUT_AMOUNT or float(amount).is_integer()) \
            and (quantity is None or quantity.amountMin <= amount <= quantity.amountMax)

    def __unicode__(self):
        return self.name


class IngredientGroup(models.Model):
    name = models.CharField(max_length=255)
    foodType = models.ForeignKey(FoodType)
    store = models.ForeignKey(Store)

    maximum = models.PositiveIntegerField(default=0, verbose_name='Maximum amount')
    minimum = models.PositiveIntegerField(default=0, verbose_name='Minimum amount')
    priority = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(default=-1, max_digits=7, decimal_places=2)

    def clean(self):
        if self.minimum > self.maximum:
            raise ValidationError('Minimum cannot be higher than maximum.')

    def save(self, *args, **kwargs):
        self.clean()
        super(IngredientGroup, self).save(*args, **kwargs)

    @staticmethod
    def checkIngredients(ingredients, food):
        '''
        Check whether the given ingredients can be made into an OrderedFood based on the closest food.
        '''

        ingredientGroups = {}
        for ingredient in ingredients:
            group = ingredient.group
            amount = 1
            if group.id in ingredientGroups:
                amount += ingredientGroups[group.id]
            if group.maximum > 0 and amount > group.maximum:
                raise IngredientGroupMaxExceeded()
            ingredientGroups[group.id] = amount

        foodTypeGroups = food.foodType.ingredientgroup_set.all()

        for ingredientGroup in ingredientGroups:
            for foodTypeGroup in foodTypeGroups:
                if foodTypeGroup.id == ingredientGroup:
                    break
            else:
                raise InvalidIngredientLinking()

        originalIngredients = food.ingredients.all()

        for ingredient in originalIngredients:
            group = ingredient.group
            if group.minimum > 0:
                inGroups = group.id in ingredientGroups
                if not inGroups:
                    raise IngredientGroupsMinimumNotMet()
                amount = ingredientGroups[group.id]

                if amount < group.minimum:
                    raise IngredientGroupsMinimumNotMet()

    @cached_property
    def ingredients(self):
        return self.ingredient_set.all()

    def __unicode__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    icon = models.PositiveIntegerField(choices=ICONS, default=0)
    alwaysVisible = models.BooleanField(default=False)

    group = models.ForeignKey(IngredientGroup)
    store = models.ForeignKey(Store)

    lastModified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.store != self.group.store:
            raise InvalidStoreLinking()
        super(Ingredient, self).save(*args, **kwargs)

    def __unicode__(self):
        return '#{id} {name} ({group})'.format(
            id=self.id,
            name=self.name,
            group=self.group
        )


class FoodCategory(models.Model):
    name = models.CharField(max_length=255)
    priority = models.PositiveIntegerField(default=0)
    store = models.ForeignKey(Store)

    class Meta:
        verbose_name_plural = 'Food categories'

    def __unicode__(self):
        return self.name


class Quantity(models.Model):
    foodType = models.ForeignKey(FoodType)
    store = models.ForeignKey(Store)
    amountMin = models.DecimalField(decimal_places=3, max_digits=7, default=1)
    amountMax = models.DecimalField(decimal_places=3, max_digits=7, default=10)
    lastModified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('foodType', 'store',)
        verbose_name_plural = 'Quantities'

    def clean(self):
        if self.amountMin > self.amountMax:
            raise ValidationError('Amount maximum need to be greater or equal to its minimum.')
        if not self.foodType.isValidAmount(self.amountMin) \
            or not self.foodType.isValidAmount(self.amountMax):
            raise InvalidFoodTypeAmount()

    def save(self, *args, **kwargs):
        self.clean()
        super(Quantity, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{amountMin}-{amountMax}'.format(
            amountMin=self.amountMin,
            amountMax=self.amountMax
        )


class Food(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(decimal_places=3, max_digits=7, default=1)
    cost = models.DecimalField(decimal_places=2, max_digits=7)
    foodType = models.ForeignKey(FoodType)
    minDays = models.PositiveIntegerField(default=0)
    canComment = models.BooleanField(default=False)
    priority = models.BigIntegerField(default=0)

    category = models.ForeignKey(FoodCategory)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRelation', blank=True)
    store = models.ForeignKey(Store)

    lastModified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    objects = LunchbreakManager()

    class Meta:
        verbose_name_plural = 'Food'

    @cached_property
    def ingredientGroups(self):
        return self.foodType.ingredientgroup_set.filter(
            store_id=self.store_id
        ).order_by('-priority', 'name')

    @cached_property
    def hasIngredients(self):
        return self.ingredients.count() > 0

    @cached_property
    def quantity(self):
        try:
            return Quantity.objects.get(foodType_id=self.foodType_id, store_id=self.store_id)
        except Quantity.DoesNotExist:
            return None

    def canOrder(self, pickupTime):
        return self.minDays == 0 \
            or (
                pickupTime - datetime.now() > timedelta(days=self.minDays)
                and datetime.now().time() < self.store.orderTime
            )

    def save(self, *args, **kwargs):
        if not self.foodType.isValidAmount(self.amount):
            raise InvalidFoodTypeAmount()
        if self.category.store_id != self.store_id:
            raise InvalidStoreLinking()

        super(Food, self).save(*args, **kwargs)

        if self.deleted:
            self.delete()

    def delete(self, *args, **kwargs):
        if self.orderedfood_set.exclude(order__status__in=ORDER_ENDED).count() == 0:
            super(Food, self).delete(*args, **kwargs)
        elif not self.deleted:
            self.deleted = True
            self.save()

    def __unicode__(self):
        return self.name


class IngredientRelation(models.Model):
    food = models.ForeignKey(Food)
    ingredient = models.ForeignKey(Ingredient)
    typical = models.BooleanField(default=False)

    class Meta:
        unique_together = ('food', 'ingredient',)

    def save(self, *args, **kwargs):
        if self.food.store_id != self.ingredient.store_id:
            raise InvalidStoreLinking()
        super(IngredientRelation, self).save(*args, **kwargs)


def tokenGenerator():
        return ''.join(random.choice(TOKEN_IDENTIFIER_CHARS) for a in xrange(TOKEN_IDENTIFIER_LENGTH))


class BaseToken(BareDevice):
    device = models.CharField(max_length=255)
    identifier = models.CharField(max_length=TOKEN_IDENTIFIER_LENGTH, default=tokenGenerator)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.device
