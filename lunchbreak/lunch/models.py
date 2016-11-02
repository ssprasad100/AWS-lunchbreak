from collections import defaultdict
from datetime import datetime, time, timedelta

import googlemaps
import pendulum
from customers.config import ORDER_STATUSES_ACTIVE
from customers.exceptions import (PastOrderDenied, PreorderTimeExceeded,
                                  StoreClosed)
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import MinValueValidator
from django.db import DatabaseError, models
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from imagekit.models import ImageSpecField
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.fields import RoundingDecimalField
from Lunchbreak.mixins import CleanModelMixin
from openpyxl import load_workbook
from polaroid.models import Polaroid
from private_media.storages import PrivateMediaStorage
from push_notifications.models import BareDevice

from .config import (CCTLDS, COST_GROUP_ALWAYS, COST_GROUP_CALCULATIONS,
                     COUNTRIES, INPUT_AMOUNT, INPUT_TYPES, LANGUAGES, WEEKDAYS)
from .exceptions import (AddressNotFound, IngredientGroupMaxExceeded,
                         IngredientGroupsMinimumNotMet, InvalidFoodTypeAmount,
                         LinkingError)
from .managers import (BaseTokenManager, FoodManager, HolidayPeriodQuerySet,
                       PeriodQuerySet, StoreManager)
from .specs import HDPI, LDPI, MDPI, XHDPI, XXHDPI, XXXHDPI
from .utils import timezone_for_store


class StoreCategory(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )

    class Meta:
        verbose_name = _('winkelcategorie')
        verbose_name_plural = _('winkelcategorieën')

    def __str__(self):
        return self.name


class StoreHeader(Polaroid):
    store = models.OneToOneField(
        'Store',
        on_delete=models.CASCADE,
        related_name='header',
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    original = models.ImageField(
        storage=PrivateMediaStorage(),
        upload_to='storeheader',
        verbose_name=_('origineel'),
        help_text=_('De originele afbeelding die werd geüpload.')
    )
    ldpi = ImageSpecField(
        spec=LDPI,
        source='original',
    )
    mdpi = ImageSpecField(
        spec=MDPI,
        source='original',
    )
    hdpi = ImageSpecField(
        spec=HDPI,
        source='original',
    )
    xhdpi = ImageSpecField(
        spec=XHDPI,
        source='original',
    )
    xxhdpi = ImageSpecField(
        spec=XXHDPI,
        source='original',
    )
    xxxhdpi = ImageSpecField(
        spec=XXXHDPI,
        source='original',
    )

    class Meta:
        verbose_name = _('headerafbeelding')
        verbose_name_plural = _('headerafbeeldingen')

    def __str__(self):
        return _('Headerafbeelding voor %(store)s') % {
            'store': self.store
        }


class AbstractAddress(models.Model, DirtyFieldsMixin):
    country = models.CharField(
        max_length=255,
        verbose_name=_('land'),
        help_text=_('Land.')
    )
    province = models.CharField(
        max_length=255,
        verbose_name=_('provincie'),
        help_text=_('Provincie.')
    )
    city = models.CharField(
        max_length=255,
        verbose_name=_('stad'),
        help_text=_('Stad.')
    )
    postcode = models.CharField(
        max_length=20,
        verbose_name=_('postcode'),
        help_text=_('Postcode.')
    )
    street = models.CharField(
        max_length=255,
        verbose_name=_('straat'),
        help_text=_('Straat.')
    )
    number = models.CharField(
        max_length=10,
        verbose_name=_('straatnummer'),
        help_text=_('Straatnummer.')
    )

    latitude = RoundingDecimalField(
        decimal_places=7,
        max_digits=10,
        verbose_name=_('breedtegraad'),
        help_text=_('Breedtegraad.')
    )
    longitude = RoundingDecimalField(
        decimal_places=7,
        max_digits=10,
        verbose_name=_('lengtegraad'),
        help_text=_('Lengtegraad.')
    )

    class Meta:
        abstract = True

    @classmethod
    def maps_client(cls):
        return googlemaps.Client(
            key=settings.GOOGLE_CLOUD_SECRET,
            connect_timeout=5,
            read_timeout=5,
            retry_timeout=1
        )

    @classmethod
    def geocode(cls, address):
        google_client = cls.maps_client()
        results = google_client.geocode(
            address=address
        )

        if len(results) == 0:
            raise AddressNotFound(
                _('No results found for given address.')
            )

        result = results[0]
        latitude = result['geometry']['location']['lat']
        longitude = result['geometry']['location']['lng']

        return latitude, longitude

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields()
        fields = [
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'latitude',
            'longitude'
        ]

        if self.pk is None or dirty_fields:
            update_location = False
            if self.pk is not None and dirty_fields:
                for field in fields:
                    if field in dirty_fields:
                        update_location = True
                        break
            else:
                update_location = True

            if update_location:
                self.clean_fields(
                    exclude=[
                        'latitude',
                        'longitude'
                    ]
                )
                self.update_location()

        self.full_clean()
        super(AbstractAddress, self).save(*args, **kwargs)

    def update_location(self):
        """Update the longitude and latitude based on the address."""
        address = '{country}, {province}, {street} {number}, {postcode} {city}'.format(
            country=self.country,
            province=self.province,
            street=self.street,
            number=self.number,
            postcode=self.postcode,
            city=self.city,
        )

        self.latitude, self.longitude = self.geocode(address=address)


class Store(AbstractAddress):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )

    categories = models.ManyToManyField(
        StoreCategory,
        verbose_name=_('winkelcategorieën'),
        help_text=_('Winkelcategorieën.')
    )
    wait = models.DurationField(
        default=timedelta(seconds=60),
        verbose_name=_('wachttijd'),
        help_text=_('Minimum tijd dat op voorhand besteld moet worden.')
    )
    preorder_time = models.TimeField(
        default=time(hour=12),
        verbose_name=_('tijd voorafgaande bestelling'),
        help_text=_(
            'Indien bepaalde waren meer dan een dag op voorhand besteld moeten '
            'worden, moeten ze voor dit tijdstip besteld worden.'
        )
    )
    hearts = models.ManyToManyField(
        'customers.User',
        through='customers.Heart',
        blank=True,
        verbose_name=_('hartjes'),
        help_text=_('Hartjes van klanten.')
    )
    seats_max = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name=_('maximum plaatsen'),
        help_text=_('Maximum aantal plaatsen voor reservaties.')
    )
    regions = models.ManyToManyField(
        'Region',
        blank=True,
        verbose_name=_('regio\'s'),
        help_text=_('Regio\'s waaraan geleverd wordt.')
    )
    timezone = models.CharField(
        max_length=255,
        default='UTC',
        verbose_name=_('tijdzone'),
        help_text=_('Tijdzone.')
    )

    online_payments_enabled = models.BooleanField(
        default=True,
        verbose_name=_('online betalingen ingeschakeld'),
        help_text=_(
            'Online betalingen ingeschakeld, er moet een GoCardless '
            'account/merchant gelinked worden voor online betalingen '
            'aanvaard kunnen worden.'
        )
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=_('Wanneer deze winkel laatst aangepast werd.')
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name=_('ingeschakeld'),
        help_text=_('Ingeschakeld.')
    )

    objects = StoreManager()

    class Meta:
        verbose_name = _('winkel')
        verbose_name_plural = _('winkels')

    def __str__(self):
        return self.name

    @cached_property
    def category(self):
        return self.categories.all()[0]

    @cached_property
    def does_delivery(self):
        return self.regions.all().exists()

    @cached_property
    def hearts_count(self):
        return self.hearts.count()

    def update_location(self):
        super().update_location()

        google_client = self.maps_client()
        result = google_client.timezone(
            location={
                'lat': self.latitude,
                'lng': self.longitude
            },
            language='English'
        )

        self.timezone = result['timeZoneId']

    def open_weekdays(self, openingperiods=None, **kwargs):
        """Wrapper for openingperiods_for returning the weekdays.

        Will use given openingperiods instead of using openingperiods_for if not None.
        Else it will use openingperiods_for with given kwargs.

        Args:
            **kwargs (dict): Passed onto openingperiods_for.
            openingperiods (list, optional): List of :obj:`pendulum.Period`s.

        Returns:
            set: Weekdays of the openingperiods.
        """
        if openingperiods is None:
            openingperiods = self.openingperiods_for(**kwargs)

        weekdays = list()
        for openingperiod in openingperiods:
            if openingperiod.start.isoweekday() not in weekdays:
                weekdays.append(openingperiod.start.isoweekday())
            if openingperiod.end.isoweekday() not in weekdays:
                weekdays.append(openingperiod.end.isoweekday())

        return weekdays

    def periods_per_weekday(self, periods=None, **kwargs):
        """Split periods into their starting weekdays.

        Return a dict with as keys the starting weekdays and values a set of
        periods with that starting weekday.

        Args:
            **kwargs (dict): Kwargs passed onto openingperiods_for if periods is None.
            periods (:obj:`list`, optional): List of :obj:`pendulum.Period`s.

        Returns:
            dict: Key: weekday of start, value set of periods
        """
        if periods is None:
            periods = self.openingperiods_for(
                **kwargs
            )

        result = defaultdict(set)

        for period in periods:
            result[period.start.isoweekday()].add(period)

        return result

    @property
    def openingperiods_today(self):
        """Wrapper for openingperiods_for_day where the datetime is the given current day."""
        return self.openingperiods_for_day(
            dt=timezone.now()
        )

    def openingperiods_for_day(self, dt, **kwargs):
        """Wrapper for opening_periods where period is the whole given day."""
        start = pendulum.instance(dt).hour_(0).minute_(0).second_(0)
        end = start.hour_(23).minute_(59).second_(59)
        period = pendulum.Period(
            start=start,
            end=end
        )

        return self.openingperiods_for(
            period=period,
            **kwargs
        )

    def openingperiods_for(self, period=None, start=None, **kwargs):
        """Get opening periods for given period.

        Return a list of periods indicating when the store is open for the given period.
        If period is None, it will use start as the start of the period.
        If start is None, it will use the current datetime + Store.wait as the start of the period.
        It will pass **kwargs onto pendulum.Pendulum.add calculate an end to
        the period based on the start.

        Args:
            **kwargs (dict): Passed onto pendulum.Pendulum.add to calculate the
            end of the period based off of the start.
            period (:obj:`pendulum.Period`, optional): Period for which the
            openingperiods are requested.
            start (:obj:`pendulum.Pendulum`, optional): Start of the period.

        Returns:
            list: List of :obj:`pendulum.Period` indicating when the store is open.

        Raises:
            ValueError: A period or start or kwargs must be given.
        """
        if period is None and start is None and not kwargs:
            raise ValueError(
                'A period or start or kwargs must be given.'
            )

        if period is None:
            if start is None:
                start = pendulum.instance(timezone.now())
                start += self.wait
            end = start.add(**kwargs)

            period = pendulum.Period(
                start=start,
                end=end
            )

        openingperiods = OpeningPeriod.objects.filter(
            store=self
        ).between(
            period=period
        )
        holidayperiods = HolidayPeriod.objects.filter(
            store=self
        ).between(
            period=period
        ).periods()

        closingperiods = []
        for period in holidayperiods:
            if not period.closed:
                openingperiods.append(period)
            else:
                closingperiods.append(period)

        result = []
        for openingperiod in openingperiods:
            result.extend(
                openingperiod.exclude(
                    *closingperiods
                )
            )
        return result

    def delivers_to(self, address):
        return self.regions.filter(
            postcode=address.postcode
        ).exists()

    def is_open(self, dt, raise_exception=True, now=None):
        """Check whether the store is open at the specified time."""

        if isinstance(dt, pendulum.Pendulum):
            dt = dt._datetime

        now = timezone.now() if now is None else now

        if dt < now:
            if not raise_exception:
                return False
            raise PastOrderDenied()

        if dt - now < self.wait:
            if not raise_exception:
                return False
            raise PreorderTimeExceeded()

        holidayperiods = HolidayPeriod.objects.filter(
            store=self,
            start__lte=dt,
            end__gte=dt
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
                if not raise_exception:
                    return False
                raise StoreClosed(
                    'De winkel is exclusief gesloten vanwege een vakantieperiode.'
                )

            periods = self.openingperiods_for_day(
                dt=dt
            )

            for period in periods:
                if dt in period:
                    return True

            if not raise_exception:
                return False
            raise StoreClosed()
        return True


class Region(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    country = models.PositiveSmallIntegerField(
        choices=COUNTRIES,
        verbose_name=_('land'),
        help_text=_('Land.')
    )
    postcode = models.CharField(
        max_length=255,
        verbose_name=_('postcode'),
        help_text=_('Postcode.')
    )

    class Meta:
        verbose_name = _('regio')
        verbose_name_plural = _('regio\'s')
        unique_together = ('country', 'postcode',)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.validate_unique()
            self.clean_fields(
                exclude=[
                    'name'
                ]
            )

            google_client = googlemaps.Client(
                key=settings.GOOGLE_CLOUD_SECRET,
                connect_timeout=5,
                read_timeout=5,
                retry_timeout=1
            )
            results = google_client.geocode(
                address=self.postcode,
                components={
                    'country': self.get_country_display()
                },
                region=CCTLDS[self.country],
                language=LANGUAGES[self.country]
            )
            if len(results) == 0:
                raise AddressNotFound(
                    _('No results found for given postcode and country.')
                )
            address_components = results[0].get('address_components', [])
            found = False
            for comp in address_components:
                types = comp.get('types', [])
                if 'locality' in types:
                    self.name = comp['long_name']
                    found = True
            if not found:
                raise AddressNotFound(
                    _('No region found for given postcode and country.')
                )

        self.full_clean()
        super(Region, self).save(*args, **kwargs)

    def __str__(self):
        return '{country}, {name} {postcode}'.format(
            country=self.get_country_display(),
            name=self.name,
            postcode=self.postcode
        )


class Period(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    day = models.PositiveSmallIntegerField(
        choices=WEEKDAYS,
        verbose_name=_('weekdag'),
        help_text=_('Dag van de week.')
    )
    time = models.TimeField(
        verbose_name=_('openingstijd'),
        help_text=_('Tijdstip waarop de winkel opengaat.')
    )
    duration = models.DurationField(
        verbose_name=_('openingsduur'),
        help_text=_('Hoelang de winkel open is vanaf de openingstijd.')
    )

    objects = PeriodQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.store.save()
        super(Period, self).save(*args, **kwargs)

    @property
    def weekdays(self):
        now = pendulum.now().with_time(
            hour=self.time.hour,
            minute=self.time.minute,
            second=self.time.second,
            microsecond=self.time.microsecond
        )
        start = now.subtract(
            days=now.isoweekday()
        ).add(
            days=self.day
        )
        period = pendulum.Period(
            start=start,
            end=start + self.duration
        )

        result = set()
        for day in period.xrange('days'):
            weekday = day.isoweekday()
            if weekday in result:
                break
            result.add(weekday)
        return result

    def start(self, day):
        if isinstance(day, datetime):
            day = pendulum.instance(day)
        if day.isoweekday() != self.day:
            day = day.subtract(
                days=day.isoweekday() + (7 if day.isoweekday() < self.day else 0)
            ).add(
                days=self.day
            )

        return day.with_time(
            hour=self.time.hour,
            minute=self.time.minute,
            second=self.time.second,
            microsecond=self.time.microsecond
        ).timezone_(
            self.store.timezone
        )

    def end(self, day):
        return self.start(day) + self.duration

    def period(self, day):
        return pendulum.Period(
            start=self.start(day),
            end=self.end(day)
        )

    @classmethod
    def weekday_as_datetime(cls, weekday, time, store):
        if weekday is None or time is None or store is None:
            return None

        now = pendulum.now(store.timezone)
        start = now.subtract(
            days=now.isoweekday()
        ).add(
            days=weekday
        )
        result = start.with_time(
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond
        )
        if result.date() < pendulum.now(store.timezone).date():
            result = result.add(
                days=7
            )
        return result

    def __str__(self):
        return '{day} {time} - {duration}'.format(
            day=self.get_day_display(),
            time=self.time,
            duration=self.duration
        )


class OpeningPeriod(Period):

    class Meta:
        verbose_name = _('openingstijd')
        verbose_name_plural = _('openingstijden')


class DeliveryPeriod(Period):

    class Meta:
        verbose_name = _('leveringstijd')
        verbose_name_plural = _('leveringstijden')


class HolidayPeriod(CleanModelMixin, models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('beschrijving'),
        help_text=_('Beschrijving met een reden.')
    )

    start = models.DateTimeField(
        verbose_name=_('start'),
        help_text=_('Start van de vakantieperiode.')
    )
    end = models.DateTimeField(
        verbose_name=_('einde'),
        help_text=_('Einde van de vakantieperiode.')
    )

    closed = models.BooleanField(
        default=True,
        verbose_name=_('gesloten'),
        help_text=_('Of de winkel gesloten is tijdens deze vakantieperiode.')
    )

    objects = HolidayPeriodQuerySet.as_manager()

    class Meta:
        verbose_name = _('vakantieperiode')
        verbose_name_plural = _('vakantieperiodes')

    @property
    def period(self):
        period = pendulum.Period(
            start=self.start,
            end=self.end
        )
        period.closed = self.closed
        return period

    def clean_start(self):
        self.start = timezone_for_store(
            value=self.start,
            store=self.store
        )
        # Put here because both the start and end need to be set to the same timezone
        self.end = timezone_for_store(
            value=self.end,
            store=self.store
        )

        if self.start >= self.end:
            raise LunchbreakException(
                'Het begin moet voor het einde zijn.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.store.save()
        super(HolidayPeriod, self).save(*args, **kwargs)

    def __str__(self):
        return '{start}-{end} {state}'.format(
            start=self.start,
            end=self.end,
            state='closed' if self.closed else 'open'
        )


class FoodType(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    quantifier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('eenheid'),
        help_text=_('Naam van de eenheid van eten, vb: "broodjes", "broden"...')
    )
    inputtype = models.PositiveIntegerField(
        choices=INPUT_TYPES,
        default=INPUT_TYPES[0][0],
        verbose_name=_('invoer type'),
        help_text=_(
            'Invoer type die aanduid hoe de hoeveelheid ingegeven moet en '
            'kan worden.'
        )
    )
    customisable = models.BooleanField(
        default=False,
        verbose_name=_('aanpasbaar'),
        help_text=_('Of dit type etenswaar aanpasbaar kan zijn.')
    )

    class Meta:
        verbose_name = _('type etenswaar')
        verbose_name_plural = _('type etenswaren')

    def is_valid_amount(self, amount, quantity=None, raise_exception=True):
        is_valid = (
            amount > 0 and (
                self.inputtype != INPUT_AMOUNT or
                float(amount).is_integer()
            ) and (
                quantity is None or
                quantity.minimum <= amount <= quantity.maximum
            )
        )

        if not is_valid and raise_exception:
            raise InvalidFoodTypeAmount()
        return is_valid

    def __str__(self):
        return self.name


class IngredientGroup(CleanModelMixin, models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    foodtype = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE,
        verbose_name=_('type etenswaar'),
        help_text=_('Type etenswaar.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    minimum = models.PositiveIntegerField(
        default=0,
        verbose_name=_('minimum'),
        help_text=_('Minimum hoeveelheid.')
    )
    maximum = models.PositiveIntegerField(
        default=0,
        verbose_name=_('maximum'),
        help_text=_('Maximum hoeveelheid.')
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name=_('prioriteit'),
        help_text=_('Prioriteit waarop gesorteerd wordt.')
    )
    cost = RoundingDecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        verbose_name=_('basisprijs'),
        help_text=_(
            'Basisprijs indien toegevoegd of afgetrokken van het etenswaar.'
        )
    )
    calculation = models.PositiveIntegerField(
        choices=COST_GROUP_CALCULATIONS,
        default=COST_GROUP_ALWAYS,
        verbose_name=_('prijsberekening'),
        help_text=_(
            'Manier waarop de prijs moet berekened worden indien '
            'ingrediënten aangepast toegevoegd of afgetrokken worden.'
        )
    )

    class Meta:
        verbose_name = _('ingrediëntengroep')
        verbose_name_plural = _('ingrediëntengroepen')

    def clean_minimum(self):
        if self.minimum > self.maximum:
            raise LunchbreakException(
                'Het minimum kan niet groter zijn dan het maximum.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(IngredientGroup, self).save(*args, **kwargs)

    @staticmethod
    def check_ingredients(ingredients, food):
        """
        Check whether the given ingredients can be made into an OrderedFood
        based on the closest food.
        """

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
                raise LinkingError()

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

    def __str__(self):
        return self.name


class Ingredient(models.Model, DirtyFieldsMixin):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=('Naam.')
    )
    cost = RoundingDecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name=_('basisprijs'),
        help_text=(
            'Basisprijs diet in rekening wordt gebracht afhankelijk van de '
            'prijsberekening ingesteld op de ingrediëntengroep.'
        )
    )

    group = models.ForeignKey(
        IngredientGroup,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name=_('ingrediëntengroep'),
        help_text=('Ingrediëntengroep.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=('Winkel.')
    )

    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=('Laatst aangepast.')
    )

    class Meta:
        verbose_name = _('ingrediënt')
        verbose_name_plural = _('ingrediënt')

    def save(self, *args, **kwargs):
        if self.store != self.group.store:
            raise LinkingError()

        if self.pk is not None:
            dirty_fields = self.get_dirty_fields(check_relationship=True)
            if 'group' in dirty_fields:
                for food in self.food_set.all():
                    food.update_typical()

        super(Ingredient, self).save(*args, **kwargs)

    def __str__(self):
        return '{name} ({group}) #{id}'.format(
            name=self.name,
            group=self.group,
            id=self.id
        )


class Menu(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=('Naam.')
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name=_('prioriteit'),
        help_text=('Prioriteit.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='menus',
        verbose_name=_('winkel'),
        help_text=('Winkel.')
    )

    class Meta:
        unique_together = ('name', 'store',)
        verbose_name = _('menu')
        verbose_name_plural = _('menu\'s')

    def __str__(self):
        return self.name


class Quantity(CleanModelMixin, models.Model):
    foodtype = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE,
        verbose_name=_('type etenswaar'),
        help_text=('Type etenswaar.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=('Winkel.')
    )

    minimum = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=1,
        verbose_name=_('minimum'),
        help_text=('Minimum hoeveelheid.')
    )
    maximum = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=10,
        verbose_name=_('maximum'),
        help_text=('Maximum hoeveelheid.')
    )

    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=('Laatst aangepast.')
    )

    class Meta:
        unique_together = ('foodtype', 'store',)
        verbose_name = _('hoeveelheid')
        verbose_name_plural = _('hoeveelheden')

    def clean_minimum(self):
        self.foodtype.is_valid_amount(self.minimum)
        if self.minimum > self.maximum:
            raise InvalidFoodTypeAmount(
                'Het minimum kan niet groter zijn dan het maximum.'
            )

    def clean_maximum(self):
        self.foodtype.is_valid_amount(self.maximum)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Quantity, self).save(*args, **kwargs)

    def __str__(self):
        return '{minimum}-{maximum}'.format(
            minimum=self.minimum,
            maximum=self.maximum
        )


class Food(CleanModelMixin, models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('naam'),
        help_text=('Naam.')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('beschrijving'),
        help_text=('Beschrijving.')
    )
    amount = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=1,
        verbose_name=_('standaardhoeveelheid'),
        help_text=('Hoeveelheid die standaard is ingevuld.')
    )
    cost = RoundingDecimalField(
        decimal_places=2,
        max_digits=7,
        verbose_name=_('basisprijs'),
        help_text=(
            'Basisprijs, dit is inclusief de gekozen ingrediënten en '
            'ingrediëntengroepen.'
        )
    )
    foodtype = models.ForeignKey(
        FoodType,
        on_delete=models.CASCADE,
        verbose_name=_('type etenswaar'),
        help_text=('Type etenswaar.')
    )
    preorder_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_('dagen op voorhand bestellen'),
        help_text=(
            'Minimum dagen op voorhand bestellen voor het uur ingesteld op de '
            'winkel.'
        )
    )
    commentable = models.BooleanField(
        default=False,
        verbose_name=_('commentaar mogelijk'),
        help_text=(
            'Of er commentaar kan achter worden gelaten bij het bestellen.'
        )
    )
    priority = models.BigIntegerField(
        default=0,
        verbose_name=_('prioriteit'),
        help_text=('Prioriteit.')
    )

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='food',
        verbose_name=_('menu'),
        help_text=('Menu.')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRelation',
        blank=True,
        verbose_name=_('ingrediënten'),
        help_text=('Ingrediënten.')
    )
    ingredientgroups = models.ManyToManyField(
        IngredientGroup,
        blank=True,
        verbose_name=_('ingrediëntengroep'),
        help_text=('Ingrediëntengroep.')
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=('Winkel.')
    )

    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=('Laatst aangepast.')
    )
    deleted = models.BooleanField(
        default=False,
        verbose_name=_('verwijderd'),
        help_text=(
            'Duid aan of het item wacht om verwijderd te worden. Het wordt '
            'pas verwijderd wanneer er geen actieve bestellingen meer zijn '
            'met dit etenswaar.'
        )
    )

    objects = FoodManager()

    class Meta:
        verbose_name = _('etenswaar')
        verbose_name_plural = _('etenswaren')

    @cached_property
    def has_ingredients(self):
        return self.ingredients.count() > 0 or self.ingredientgroups.count() > 0

    @cached_property
    def quantity(self):
        try:
            return Quantity.objects.get(
                foodtype_id=self.foodtype_id,
                store_id=self.store_id
            )
        except Quantity.DoesNotExist:
            return None

    def update_typical(self):
        ingredientgroups = self.ingredientgroups.all()
        ingredientrelations = self.ingredientrelation_set.select_related(
            'ingredient__group'
        ).all()

        for ingredientrelation in ingredientrelations:
            ingredient = ingredientrelation.ingredient
            # Musn't the ingredient be selected before it can be typical?
            if ingredient.group not in ingredientgroups:
                if not ingredientrelation.typical:
                    ingredientrelation.typical = True
                    ingredientrelation.save()
            elif ingredientrelation.typical:
                ingredientrelation.typical = False
                ingredientrelation.save()

    def is_orderable(self, dt, now=None):
        """
        Check whether this food can be ordered for the given day.
        This does not check whether the Store.wait has been exceeded!
        """
        if self.preorder_days == 0:
            return True
        else:
            now = datetime.now() if now is None else now
            # Amount of days needed to order in advance
            # (add 1 if it isn't before the preorder_time)
            preorder_days = self.preorder_days + (
                1 if now.time() > self.store.preorder_time else 0
            )

            # Calculate the amount of days between dt and now
            difference_day = (dt - now).days
            difference_day += (
                1
                if dt.time() < now.time() and
                (now + (dt - now)).day != now.day
                else 0
            )

            return difference_day >= preorder_days

    def is_valid_amount(self, amount, raise_exception=True):
        return self.foodtype.is_valid_amount(
            amount=amount,
            quantity=self.quantity,
            raise_exception=raise_exception
        )

    def clean_amount(self):
        self.foodtype.is_valid_amount(self.amount)

    def clean_store(self):
        if self.store_id != self.menu.store_id:
            raise LinkingError(
                'De menu van het etenswaar moet van dezelfde winkel zijn als '
                'het etenswaar.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        super(Food, self).save(*args, **kwargs)

        if self.deleted:
            self.delete()

    def delete(self, *args, **kwargs):
        active_orders_amount = self.orderedfood_set.filter(
            placed_order__status__in=ORDER_STATUSES_ACTIVE
        ).count()
        if active_orders_amount == 0:
            super(Food, self).delete(*args, **kwargs)
        elif not self.deleted:
            self.deleted = True
            self.save()

    def __str__(self):
        return self.name

    @staticmethod
    def changed_ingredients(sender, instance, action=None, **kwargs):
        if action is None or len(action) > 4 and action[:4] == 'post':
            if isinstance(instance, Food):
                instance.update_typical()
            elif instance.__class__ in [Ingredient, IngredientGroup]:
                for food in instance.food_set.all():
                    food.update_typical()
            elif isinstance(instance, IngredientRelation):
                instance.food.update_typical()

    @classmethod
    def check_ingredientgroups(cls, action, instance, pk_set, **kwargs):
        if len(action) > 4 and action[:4] == 'post':
            groups = instance.ingredientgroups.filter(
                ~Q(store_id=instance.store_id)
            )
            if groups.exists():
                raise LinkingError(
                    'The food and its ingredientgroups need to belong to the same store.'
                )

    @classmethod
    def from_excel(cls, store, file):
        workbook = load_workbook(
            filename=file,
            read_only=True
        )

        if 'Food' not in workbook:
            raise LunchbreakException(
                _('The worksheet "Food" could not be found. Please use our template.')
            )

        worksheet = workbook['Food']
        mapping = [
            {
                'field_name': 'name',
            },
            {
                'field_name': 'description',
            },
            {
                'field_name': 'menu',
                'instance': {
                    'model': Menu,
                    'create': True,
                    'field_name': 'name'
                }
            },
            {
                'field_name': 'cost',
            },
            {
                'field_name': 'foodtype',
                'instance': {
                    'model': FoodType,
                    'field_name': 'name',
                    'store': False
                }
            },
            {
                'field_name': 'preorder_days',
            },
            {
                'field_name': 'priority',
            },
        ]
        mapping_length = len(mapping)

        food_list = []
        created_relations = []
        skip = True
        for row in worksheet.rows:
            # Skip headers
            if skip:
                skip = False
                continue

            kwargs = {}
            exclude = []

            for cell in row:
                if not isinstance(cell.column, int):
                    continue

                i = cell.column - 1
                if i >= mapping_length:
                    continue
                info = mapping[i]
                value = cell.value
                if 'instance' in info:
                    instance = info['instance']
                    create = instance.get('create', False)
                    model = instance['model']

                    exclude.append(info['field_name'])
                    where = {
                        instance['field_name']: cell.value
                    }
                    if instance.get('store', True):
                        where['store'] = store

                    if create:
                        value, created = model.objects.get_or_create(
                            **where
                        )
                        if created:
                            created_relations.append(value)
                    else:
                        value = model.objects.get(
                            **where
                        )

                kwargs[info['field_name']] = value

            food = Food(
                store=store,
                **kwargs
            )
            try:
                food.clean_fields(exclude=exclude)
            except LunchbreakException:
                for relation in created_relations:
                    relation.delete()
                raise LunchbreakException(
                    _('Could not import row %(row)d.') % {
                        'row': cell.row
                    }
                )

            food_list.append(food)

        try:
            cls.objects.bulk_create(food_list)
        except DatabaseError:
            for relation in created_relations:
                relation.delete()


class IngredientRelation(models.Model, DirtyFieldsMixin):
    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        verbose_name=_('etenswaar'),
        help_text=_('Etenswaar.')
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('ingrediënt'),
        help_text=_('Ingrediënt.')
    )
    selected = models.BooleanField(
        default=False,
        verbose_name=_('geselecteerd'),
        help_text=_('Of het ingrediënt standaard geselecteerd is.')
    )
    typical = models.BooleanField(
        default=False,
        verbose_name=_('typisch'),
        help_text=_('Of het een typisch ingrediënt is voor het gelinkte etenswaar.')
    )

    class Meta:
        unique_together = ('food', 'ingredient',)

    def save(self, *args, **kwargs):
        if self.food.store_id != self.ingredient.store_id:
            raise LinkingError()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'ingredient' in dirty_fields:
            self.food.update_typical()

        super(IngredientRelation, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.ingredient)


class BaseToken(BareDevice, DirtyFieldsMixin):
    device = models.CharField(
        max_length=255,
        verbose_name=_('apparaat'),
        help_text=_('Naam van het apparaat.')
    )
    identifier = models.CharField(
        max_length=255,
        verbose_name=_('idenfitifcatie'),
        help_text=_('Idenfitifcatie code die toegang geeft to Lunchbreak.')
    )

    objects = BaseTokenManager()

    class Meta:
        abstract = True,

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

    def __str__(self):
        return self.device


m2m_changed.connect(
    Food.changed_ingredients,
    sender=Food.ingredientgroups.through,
    weak=False
)
post_save.connect(
    Food.changed_ingredients,
    sender=IngredientRelation,
    weak=False
)
m2m_changed.connect(
    Food.changed_ingredients,
    sender=Food.ingredients.through,
    weak=False
)
m2m_changed.connect(
    Food.check_ingredientgroups,
    sender=Food.ingredientgroups.through,
    weak=False
)
