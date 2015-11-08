from __future__ import unicode_literals

import copy
import math
import random
from datetime import datetime, time, timedelta

import requests
from customers.config import ORDER_ENDED
from customers.exceptions import MinTimeExceeded, PastOrderDenied, StoreClosed
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import m2m_changed
from django.utils import timezone
from django.utils.functional import cached_property
from imagekit.models import ImageSpecField
from lunch.config import (COST_GROUP_ALWAYS, COST_GROUP_CALCULATIONS, DAYS,
                          ICONS, INPUT_AMOUNT, INPUT_TYPES,
                          TOKEN_IDENTIFIER_CHARS, TOKEN_IDENTIFIER_LENGTH)
from lunch.exceptions import (AddressNotFound, IngredientGroupMaxExceeded,
                              IngredientGroupsMinimumNotMet,
                              InvalidFoodTypeAmount, InvalidIngredientLinking,
                              InvalidStoreLinking)
from lunch.specs import HDPI, LDPI, MDPI, XHDPI, XXHDPI, XXXHDPI
from polaroid.models import Polaroid
from private_media.storages import PrivateMediaStorage
from push_notifications.models import BareDevice, DeviceManager


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
        return self.get_queryset().exclude(
            latitude=None
        ).exclude(
            longitude=None
        ).extra(
            select={
                'distance': haversine
            },
            select_params=[
                latitude,
                latitude,
                longitude
            ],
            where=[
                haversine_where
            ],
            params=[
                latitude,
                latitude,
                longitude,
                proximity
            ],
            order_by=[
                'distance'
            ]
        )

    def closestFood(self, ingredients, original):
        if not original.foodType.customisable:
            return original

        ingredientsIn = -1 if len(ingredients) == 0 else '''
            CASE WHEN lunch_ingredient.id IN (%s)
                THEN
                    1
                ELSE
                    -1
                END''' % ','.join([str(i.id) for i in ingredients])

        return Food.objects.raw('''
            SELECT
                lunch_food.*
            FROM
                `lunch_food`
                LEFT JOIN
                    `lunch_ingredientrelation` ON lunch_food.id = lunch_ingredientrelation.food_id
                    AND lunch_ingredientrelation.typical = 1
                LEFT JOIN
                    `lunch_ingredient` ON lunch_ingredientrelation.ingredient_id = lunch_ingredient.id
            WHERE
                lunch_food.foodType_id = %s AND
                lunch_food.store_id = %s
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
                lunch_food.id = %s DESC,
                lunch_food.cost ASC;
            ''', [
            original.foodType.id,
            original.store.id,
            ingredientsIn,
            original.id
        ])[0]


class StoreCategory(models.Model):
    name = models.CharField(
        max_length=255
    )
    icon = models.PositiveIntegerField(
        choices=ICONS,
        default=0
    )

    class Meta:
        verbose_name_plural = 'Store categories'

    def __unicode__(self):
        return self.name


class StoreHeader(Polaroid):
    original = models.ImageField(
        storage=PrivateMediaStorage(),
        upload_to='storeheader'
    )
    ldpi = ImageSpecField(
        spec=LDPI,
        source='original'
    )
    mdpi = ImageSpecField(
        spec=MDPI,
        source='original'
    )
    hdpi = ImageSpecField(
        spec=HDPI,
        source='original'
    )
    xhdpi = ImageSpecField(
        spec=XHDPI,
        source='original'
    )
    xxhdpi = ImageSpecField(
        spec=XXHDPI,
        source='original'
    )
    xxxhdpi = ImageSpecField(
        spec=XXXHDPI,
        source='original'
    )


class Store(models.Model):
    name = models.CharField(
        max_length=255
    )
    header = models.ForeignKey(
        StoreHeader,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    country = models.CharField(
        max_length=255
    )
    province = models.CharField(
        max_length=255
    )
    city = models.CharField(
        max_length=255
    )
    postcode = models.CharField(
        max_length=20,
        verbose_name='Postal code'
    )
    street = models.CharField(
        max_length=255
    )
    number = models.PositiveIntegerField()
    latitude = models.DecimalField(
        blank=True,
        decimal_places=7,
        max_digits=10
    )
    longitude = models.DecimalField(
        blank=True,
        decimal_places=7,
        max_digits=10
    )

    categories = models.ManyToManyField(StoreCategory)
    minTime = models.DurationField(
        default=timedelta(seconds=60)
    )
    orderTime = models.TimeField(
        default=time(hour=12)
    )
    hearts = models.ManyToManyField(
        'customers.User',
        through='customers.Heart',
        blank=True
    )
    maxSeats = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(1)
        ]
    )

    lastModified = models.DateTimeField(
        auto_now=True
    )
    enabled = models.BooleanField(
        default=True
    )

    objects = LunchbreakManager()

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
    def minTimeV3(self):
        return math.ceil(self.minTime.total_seconds() / 60)

    @cached_property
    def heartsCount(self):
        return self.hearts.count()

    @staticmethod
    def checkOpen(store, pickupTime, now=None):
        now = timezone.now() if now is None else now

        if pickupTime < now:
            raise PastOrderDenied()

        if pickupTime - now < store.minTime:
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
    day = models.PositiveIntegerField(
        choices=DAYS
    )

    opening = models.TimeField()
    closing = models.TimeField()

    class Meta:
        verbose_name_plural = 'Opening hours'

    def clean(self):
        if self.opening >= self.closing:
            raise ValidationError('Opening needs to be before closing.')

    def save(self, *args, **kwargs):
        self.full_clean()
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
    description = models.CharField(
        max_length=255,
        blank=True
    )

    start = models.DateTimeField()
    end = models.DateTimeField()

    closed = models.BooleanField(
        default=True
    )

    def clean(self):
        if self.start >= self.end:
            raise ValidationError('Start needs to be before end.')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.store.save()
        super(HolidayPeriod, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{start}-{end} {state}'.format(
            start=self.start,
            end=self.end,
            state='closed' if self.closed else 'open'
        )


class FoodType(models.Model):
    name = models.CharField(
        max_length=255
    )
    icon = models.PositiveIntegerField(
        choices=ICONS,
        default=ICONS[0][0]
    )
    quantifier = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    inputType = models.PositiveIntegerField(
        choices=INPUT_TYPES,
        default=INPUT_TYPES[0][0]
    )
    customisable = models.BooleanField(
        default=False
    )

    def isValidAmount(self, amount, quantity=None):
        return amount > 0 \
            and (self.inputType != INPUT_AMOUNT or float(amount).is_integer()) \
            and (quantity is None or quantity.amountMin <= amount <= quantity.amountMax)

    def __unicode__(self):
        return self.name


class IngredientGroup(models.Model):
    name = models.CharField(
        max_length=255
    )
    foodType = models.ForeignKey(FoodType)
    store = models.ForeignKey(Store)

    maximum = models.PositiveIntegerField(
        default=0,
        verbose_name='Maximum amount'
    )
    minimum = models.PositiveIntegerField(
        default=0,
        verbose_name='Minimum amount'
    )
    priority = models.PositiveIntegerField(
        default=0
    )
    cost = models.DecimalField(
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        max_digits=7,
        decimal_places=2
    )
    costCalculation = models.PositiveIntegerField(
        choices=COST_GROUP_CALCULATIONS,
        default=COST_GROUP_ALWAYS
    )

    def clean(self):
        if self.minimum > self.maximum:
            raise ValidationError('Minimum cannot be higher than maximum.')

    def save(self, *args, **kwargs):
        self.full_clean()
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


class Ingredient(models.Model, DirtyFieldsMixin):
    name = models.CharField(
        max_length=255
    )
    cost = models.DecimalField(
        default=0,
        max_digits=7,
        decimal_places=2
    )
    icon = models.PositiveIntegerField(
        choices=ICONS,
        default=0
    )

    group = models.ForeignKey(IngredientGroup)
    store = models.ForeignKey(Store)

    lastModified = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if self.store != self.group.store:
            raise InvalidStoreLinking()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'group' in dirty_fields:
            for food in self.food_set.all():
                food.updateTypicalIngredients()

        super(Ingredient, self).save(*args, **kwargs)

    def __unicode__(self):
        return '#{id} {name} ({group})'.format(
            id=self.id,
            name=self.name,
            group=self.group
        )


class FoodCategory(models.Model):
    name = models.CharField(
        max_length=255
    )
    priority = models.PositiveIntegerField(
        default=0
    )
    store = models.ForeignKey(Store)

    class Meta:
        verbose_name_plural = 'Food categories'

    def __unicode__(self):
        return self.name


class Quantity(models.Model):
    foodType = models.ForeignKey(FoodType)
    store = models.ForeignKey(Store)

    amountMin = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=1
    )
    amountMax = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=10
    )

    lastModified = models.DateTimeField(
        auto_now=True
    )

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
        self.full_clean()
        super(Quantity, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{amountMin}-{amountMax}'.format(
            amountMin=self.amountMin,
            amountMax=self.amountMax
        )


class Food(models.Model):
    name = models.CharField(
        max_length=255
    )
    description = models.TextField(
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
    foodType = models.ForeignKey(FoodType)
    minDays = models.PositiveIntegerField(
        default=0
    )
    canComment = models.BooleanField(
        default=False
    )
    priority = models.BigIntegerField(
        default=0
    )

    category = models.ForeignKey(FoodCategory)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRelation',
        blank=True
    )
    ingredientGroups = models.ManyToManyField(
        IngredientGroup,
        blank=True
    )
    store = models.ForeignKey(Store)

    lastModified = models.DateTimeField(
        auto_now=True
    )
    deleted = models.BooleanField(
        default=False
    )
    objects = LunchbreakManager()

    class Meta:
        verbose_name_plural = 'Food'

    @cached_property
    def hasIngredients(self):
        return self.ingredients.count() > 0

    @cached_property
    def quantity(self):
        try:
            return Quantity.objects.get(
                foodType_id=self.foodType_id,
                store_id=self.store_id
            )
        except Quantity.DoesNotExist:
            return None

    @staticmethod
    def ingredientChange(sender, instance, action, reverse, model, pk_set, using, **kwargs):
        if len(action) > 4 and action[:4] == 'post':
            if isinstance(instance, Food):
                instance.updateTypicalIngredients()
            elif instance.__class__ in [Ingredient, IngredientGroup]:
                for food in instance.food_set.all():
                    food.updateTypicalIngredients()

    def updateTypicalIngredients(self):
        ingredientGroups = self.ingredientGroups.all()
        ingredientRelations = self.ingredientrelation_set.select_related('ingredient__group').all()

        for ingredientRelation in ingredientRelations:
            ingredient = ingredientRelation.ingredient
            if ingredient.group not in ingredientGroups:
                if not ingredientRelation.typical:
                    ingredientRelation.typical = True
                    ingredientRelation.save()
            elif ingredientRelation.typical:
                ingredientRelation.typical = False
                ingredientRelation.save()

    def canOrder(self, pickupTime, now=None):
        '''
        Check whether this food can be ordered for the given day.
        This does not check whether the Store.minTime has been exceeded!
        '''
        if self.minDays == 0:
            return True
        else:
            now = datetime.now() if now is None else now
            # Amount of days needed to order in advance
            # (add 1 if it isn't before the orderTime)
            minDays = self.minDays + (1 if now.time() > self.store.orderTime else 0)

            # Calculate the amount of days between pickup and now
            dayDifference = (pickupTime - now).days
            dayDifference += (
                1
                if pickupTime.time() < now.time()
                and (now + (pickupTime - now)).day != now.day
                else 0
            )

            return dayDifference >= minDays

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


class IngredientRelation(models.Model, DirtyFieldsMixin):
    food = models.ForeignKey(Food)
    ingredient = models.ForeignKey(Ingredient)
    selected = models.BooleanField(
        default=False
    )
    typical = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ('food', 'ingredient',)

    def save(self, *args, **kwargs):
        if self.food.store_id != self.ingredient.store_id:
            raise InvalidStoreLinking()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'ingredient' in dirty_fields:
            self.food.updateTypicalIngredients()

        super(IngredientRelation, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.ingredient)


def tokenGenerator():
        return ''.join(random.choice(TOKEN_IDENTIFIER_CHARS) for a in xrange(TOKEN_IDENTIFIER_LENGTH))


class BaseTokenManager(DeviceManager):
    def createToken(self, arguments, defaults, clone=False):
        rawIdentifier = tokenGenerator()
        defaults['identifier'] = rawIdentifier

        try:
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )
        except MultipleObjectsReturned:
            self.filter(**arguments).delete()
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )

        if clone:
            tokenCopy = copy.copy(token)
            tokenCopy.identifier = rawIdentifier
            return (tokenCopy, created,)
        return (token, created,)


class BaseToken(BareDevice, DirtyFieldsMixin):
    device = models.CharField(
        max_length=255
    )
    identifier = models.CharField(
        max_length=255
    )

    objects = BaseTokenManager()

    def save(self, *args, **kwargs):
        forceHashing = kwargs.pop('forceHashing', False)

        if self.pk is None or self.is_dirty() or forceHashing:
            dirtyIdentifier = self.get_dirty_fields().get('identifier', None)

            if self.pk is None or dirtyIdentifier is not None or forceHashing:
                self.identifier = make_password(self.identifier, hasher='sha1')

        super(BaseToken, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def checkIdentifier(self, rawIdentifier):
        return check_password(rawIdentifier, self.identifier)

    def __unicode__(self):
        return self.device


m2m_changed.connect(Food.ingredientChange, sender=Food.ingredientGroups.through)
m2m_changed.connect(Food.ingredientChange, sender=Food.ingredients.through)
