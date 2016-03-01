from __future__ import unicode_literals

import copy
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
                          ICONS, INPUT_AMOUNT, INPUT_TYPES, random_token)
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
        # d = 2 * r * asin(
        #   sqrt(
        #       sin^2(
        #           ( lat2-lat1 ) / 2
        #       ) + cos(lat1)*cos(lat2)*sin^2(
        #           (lon2-lon1) / 2
        #       )
        #   )
        # )
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

    def closest(self, ingredients, original):
        if not original.foodtype.customisable:
            return original

        ingredients_in = -1 if len(ingredients) == 0 else '''
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
                lunch_food.foodtype_id = %s AND
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
            original.foodtype.id,
            original.store.id,
            ingredients_in,
            original.id
        ])[0]


class StoreCategory(models.Model):
    name = models.CharField(
        max_length=255
    )
    icon = models.PositiveIntegerField(
        choices=ICONS,
        default=ICONS[0][0]
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
    number = models.CharField(
        max_length=10
    )
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
    wait = models.DurationField(
        default=timedelta(seconds=60)
    )
    preorder_time = models.TimeField(
        default=time(hour=12)
    )
    hearts = models.ManyToManyField(
        'customers.User',
        through='customers.Heart',
        blank=True
    )
    seats_max = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(1)
        ]
    )

    modified = models.DateTimeField(
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
            raise AddressNotFound(result)

        self.latitude = result['results'][0]['geometry']['location']['lat']
        self.longitude = result['results'][0]['geometry']['location']['lng']

        super(Store, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{name}, {city}'.format(
            name=self.name,
            city=self.city
        )

    @cached_property
    def hearts_count(self):
        return self.hearts.count()

    @staticmethod
    def is_open(store, pickup, now=None):
        """Check whether the store is open at the specified time."""

        now = timezone.now() if now is None else now

        if pickup < now:
            raise PastOrderDenied()

        if pickup - now < store.wait:
            raise MinTimeExceeded()

        holidayperiods = HolidayPeriod.objects.filter(
            store=store,
            start__lte=pickup,
            end__gte=pickup
        )

        closed = False
        for holidayperiod in holidayperiods:
            if not holidayperiod.closed:
                break
            else:
                closed = True
        else:
            # Open stores are
            if closed:
                raise StoreClosed()

            # datetime.weekday(): return monday 0 - sunday 6
            # datetime.strftime('%w'): return sunday 0 - monday 6
            pickup_day = pickup.strftime('%w')
            openinghours = OpeningHours.objects.filter(store=store, day=pickup_day)
            pickup_time = pickup.time()

            for o in openinghours:
                if o.opening <= pickup_time <= o.closing:
                    break
            else:
                # If the for loop is not stopped by the break, it means that the time of
                # pickup is never when the store is open.
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
    quantifier = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    inputtype = models.PositiveIntegerField(
        choices=INPUT_TYPES,
        default=INPUT_TYPES[0][0]
    )
    customisable = models.BooleanField(
        default=False
    )

    def is_valid_amount(self, amount, quantity=None):
        return (
            amount > 0 and
            (self.inputtype != INPUT_AMOUNT or float(amount).is_integer()) and
            (quantity is None or quantity.min <= amount <= quantity.max)
        )

    def __unicode__(self):
        return self.name


class IngredientGroup(models.Model):
    name = models.CharField(
        max_length=255
    )
    foodtype = models.ForeignKey(FoodType)
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
    calculation = models.PositiveIntegerField(
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
    def check_ingredients(ingredients, food):
        '''
        Check whether the given ingredients can be made into an OrderedFood
        based on the closest food.
        '''

        ingredientgroups = {}
        for ingredient in ingredients:
            group = ingredient.group
            amount = 1
            if group.id in ingredientgroups:
                amount += ingredientgroups[group.id]
            if group.maximum > 0 and amount > group.maximum:
                raise IngredientGroupMaxExceeded()
            ingredientgroups[group.id] = amount

        foodtype_groups = food.foodtype.ingredientgroup_set.all()

        for ingredientgroup in ingredientgroups:
            for foodtype_group in foodtype_groups:
                if foodtype_group.id == ingredientgroup:
                    break
            else:
                raise InvalidIngredientLinking()

        original_ingredients = food.ingredients.all()

        for ingredient in original_ingredients:
            group = ingredient.group
            if group.minimum > 0:
                in_groups = group.id in ingredientgroups
                if not in_groups:
                    raise IngredientGroupsMinimumNotMet()
                amount = ingredientgroups[group.id]

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

    group = models.ForeignKey(IngredientGroup)
    store = models.ForeignKey(Store)

    modified = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if self.store != self.group.store:
            raise InvalidStoreLinking()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'group' in dirty_fields:
            for food in self.food_set.all():
                food.update_typical()

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
    foodtype = models.ForeignKey(FoodType)
    store = models.ForeignKey(Store)

    min = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=1
    )
    max = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        default=10
    )

    modified = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('foodtype', 'store',)
        verbose_name_plural = 'Quantities'

    def clean(self):
        if self.min > self.max:
            raise ValidationError('Amount maximum need to be greater or equal to its minimum.')
        if not self.foodtype.is_valid_amount(self.min) or \
                not self.foodtype.is_valid_amount(self.max):
            raise InvalidFoodTypeAmount()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Quantity, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{min}-{max}'.format(
            min=self.min,
            max=self.max
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
    foodtype = models.ForeignKey(FoodType)
    preorder_days = models.PositiveIntegerField(
        default=0
    )
    commentable = models.BooleanField(
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
    ingredientgroups = models.ManyToManyField(
        IngredientGroup,
        blank=True
    )
    store = models.ForeignKey(Store)

    modified = models.DateTimeField(
        auto_now=True
    )
    deleted = models.BooleanField(
        default=False
    )
    objects = LunchbreakManager()

    class Meta:
        verbose_name_plural = 'Food'

    @cached_property
    def has_ingredients(self):
        return self.ingredients.count() > 0 and self.ingredientgroups.count() > 0

    @cached_property
    def quantity(self):
        try:
            return Quantity.objects.get(
                foodtype_id=self.foodtype_id,
                store_id=self.store_id
            )
        except Quantity.DoesNotExist:
            return None

    @staticmethod
    def changed_ingredients(sender, instance, action, reverse, model, pk_set, using, **kwargs):
        if len(action) > 4 and action[:4] == 'post':
            if isinstance(instance, Food):
                instance.update_typical()
            elif instance.__class__ in [Ingredient, IngredientGroup]:
                for food in instance.food_set.all():
                    food.update_typical()

    def update_typical(self):
        ingredientgroups = self.ingredientgroups.all()
        ingredientrelations = self.ingredientrelation_set.select_related(
            'ingredient__group'
        ).all()

        for ingredientrelation in ingredientrelations:
            ingredient = ingredientrelation.ingredient
            if ingredient.group not in ingredientgroups:
                if not ingredientrelation.typical:
                    ingredientrelation.typical = True
                    ingredientrelation.save()
            elif ingredientrelation.typical:
                ingredientrelation.typical = False
                ingredientrelation.save()

    def is_orderable(self, pickup, now=None):
        '''
        Check whether this food can be ordered for the given day.
        This does not check whether the Store.wait has been exceeded!
        '''
        if self.preorder_days == 0:
            return True
        else:
            now = datetime.now() if now is None else now
            # Amount of days needed to order in advance
            # (add 1 if it isn't before the preorder_time)
            preorder_days = self.preorder_days + (1 if now.time() > self.store.preorder_time else 0)

            # Calculate the amount of days between pickup and now
            difference_day = (pickup - now).days
            difference_day += (
                1
                if pickup.time() < now.time() and
                (now + (pickup - now)).day != now.day
                else 0
            )

            return difference_day >= preorder_days

    def save(self, *args, **kwargs):
        if not self.foodtype.is_valid_amount(self.amount):
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
            self.food.update_typical()

        super(IngredientRelation, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.ingredient)


class BaseTokenManager(DeviceManager):

    def create_token(self, arguments, defaults, clone=False):
        identifier_raw = random_token()
        defaults['identifier'] = identifier_raw

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
            token_copy = copy.copy(token)
            token_copy.identifier = identifier_raw
            return (token_copy, created,)
        return (token, created,)


class BaseToken(BareDevice, DirtyFieldsMixin):
    device = models.CharField(
        max_length=255
    )
    identifier = models.CharField(
        max_length=255
    )

    objects = BaseTokenManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # forced hashing can be removed when resetting migrations
        force_hashing = kwargs.pop('force_hashing', False)

        if self.pk is None or self.is_dirty() or force_hashing:
            identifier_dirty = self.get_dirty_fields().get('identifier', None)

            if self.pk is None or identifier_dirty is not None or force_hashing:
                self.identifier = make_password(self.identifier, hasher='sha1')

        super(BaseToken, self).save(*args, **kwargs)

    def check_identifier(self, identifier_raw):
        return check_password(identifier_raw, self.identifier)

    def __unicode__(self):
        return self.device


m2m_changed.connect(Food.changed_ingredients, sender=Food.ingredientgroups.through)
m2m_changed.connect(Food.changed_ingredients, sender=Food.ingredients.through)
