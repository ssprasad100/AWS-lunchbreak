from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.mixins import CleanModelMixin

from ..managers import StaffManager
from ..mixins import NotifyModelMixin
from .abstract_password import AbstractPassword


class Staff(CleanModelMixin, AbstractPassword, NotifyModelMixin):

    class Meta:
        verbose_name = _('Personeel')
        verbose_name_plural = _('Personeel')

    def __str__(self):
        return '{store}: {name}'.format(
            store=self.store,
            name=self.name
        )

    store = models.OneToOneField(
        'lunch.Store',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('e-mailadres'),
        help_text=_('E-mailadres.')
    )
    first_name = models.CharField(
        max_length=191,
        verbose_name=_('voornaam'),
        help_text=_('Voornaam.')
    )
    last_name = models.CharField(
        max_length=191,
        verbose_name=_('familienaam'),
        help_text=_('Familienaam.')
    )
    gocardless = models.OneToOneField(
        'django_gocardless.Merchant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('GoCardless account'),
        help_text=_('GoCardless account.')
    )
    payconiq = models.OneToOneField(
        'payconiq.Merchant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Payconiq account'),
        help_text=_('Payconiq account.')
    )

    objects = StaffManager()

    @cached_property
    def name(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name
        )

    @property
    def gocardless_ready(self):
        """Whether the store is ready to use GoCardless.

        Returns:
            True if the store has GoCardless enabled and has a confirmed
            GoCardless merchant linked.
            bool
        """
        return self.store.gocardless_enabled \
            and self.gocardless is not None \
            and self.gocardless.confirmed

    @property
    def payconiq_ready(self):
        """Whether the store is ready go use Payconiq.

        Returns:
            True if the store has Payconiq enabled and has a Payconiq
            merchant linked.
            bool
        """
        return self.store.payconiq_enabled \
            and self.payconiq

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def clean_email(self):
        """User lowercase emails in the database to remove duplicates."""

        if self.email is not None:
            self.email = self.email.lower()
