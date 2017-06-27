import googlemaps
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.fields import RoundingDecimalField

from ..exceptions import AddressNotFound


class AbstractAddress(models.Model, DirtyFieldsMixin):
    country = models.CharField(
        max_length=191,
        verbose_name=_('land'),
        help_text=_('Land.')
    )
    province = models.CharField(
        max_length=191,
        verbose_name=_('provincie'),
        help_text=_('Provincie.')
    )
    city = models.CharField(
        max_length=191,
        verbose_name=_('stad'),
        help_text=_('Stad.')
    )
    postcode = models.CharField(
        max_length=20,
        verbose_name=_('postcode'),
        help_text=_('Postcode.')
    )
    street = models.CharField(
        max_length=191,
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
