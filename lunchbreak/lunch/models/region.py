import googlemaps
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..config import CCTLDS, COUNTRIES, LANGUAGES
from ..exceptions import AddressNotFound


class Region(models.Model):
    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    country = models.PositiveSmallIntegerField(
        choices=COUNTRIES,
        verbose_name=_('land'),
        help_text=_('Land.')
    )
    postcode = models.CharField(
        max_length=191,
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
