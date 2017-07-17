from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.mixins import CleanModelMixin
from push_notifications.models import BareDevice

from ..managers import BaseTokenManager


class BaseToken(CleanModelMixin, BareDevice, DirtyFieldsMixin):
    device = models.CharField(
        max_length=191,
        verbose_name=_('apparaat'),
        help_text=_('Naam van het apparaat.')
    )
    identifier = models.CharField(
        max_length=191,
        verbose_name=_('identificatie'),
        help_text=_('Identificatie code die toegang geeft tot Lunchbreak.')
    )

    objects = BaseTokenManager()

    class Meta:
        abstract = True,

    def save(self, *args, **kwargs):
        self.full_clean()
        # forced hashing can be removed when resetting migrations
        force_hashing = kwargs.pop('force_hashing', False)

        if self.pk is None or self.is_dirty() or force_hashing:
            identifier_dirty = self.get_dirty_fields().get('identifier', None)

            if self.pk is None or identifier_dirty is not None or force_hashing:
                self.identifier = make_password(self.identifier, hasher='sha1')

        super(BaseToken, self).save(*args, **kwargs)

    def check_identifier(self, identifier_raw):
        return check_password(identifier_raw, self.identifier)

    def clean_device(self):
        if self.device:
            # Convert to ASCII/Punycode and convert UTF-8 characters because
            # those are not allowed in headers.
            try:
                self.device.encode(
                    'ascii'
                )
            except UnicodeEncodeError:
                self.device = self.device.encode(
                    'punycode'
                ).decode(
                    'ascii'
                )

    def __str__(self):
        return self.device
