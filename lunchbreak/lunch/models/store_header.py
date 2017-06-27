from django.db import models
from django.utils.translation import ugettext_lazy as _
from imagekit.models import ImageSpecField
from polaroid.models import Polaroid
from private_media.storages import PrivateMediaStorage

from ..specs import HDPI, LDPI, MDPI, XHDPI, XXHDPI, XXXHDPI


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.store.save()

    def __str__(self):
        return _('Headerafbeelding voor %(store)s') % {
            'store': self.store
        }
