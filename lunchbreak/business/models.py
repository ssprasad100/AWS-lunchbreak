from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import BaseToken

from .managers import StaffManager
from .mixins import NotifyModelMixin


class AbstractPasswordReset(models.Model):
    password_reset = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name=_('wachtwoord reset'),
        help_text=_('Code gebruikt om het wachtwoord te veranderen.')
    )

    class Meta:
        abstract = True


class AbstractPassword(AbstractPasswordReset):
    password = models.CharField(
        max_length=191,
        verbose_name=_('wachtwoord'),
        help_text=_('Geëncrypteerd wachtwoord.')
    )

    class Meta:
        abstract = True

    def set_password(self, password_raw):
        self.password = make_password(password_raw)

    def check_password(self, password_raw):
        return check_password(password_raw, self.password)


class Staff(AbstractPassword, NotifyModelMixin):

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


class StaffToken(BaseToken):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('personeel'),
        help_text=_('Personeel.')
    )

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE

    class Meta:
        verbose_name = _('personeelstoken')
        verbose_name_plural = _('personeelstokens')


class Employee(AbstractPassword, NotifyModelMixin):
    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        verbose_name=_('personeel'),
        help_text=_('Personeel.')
    )
    owner = models.BooleanField(
        default=False,
        verbose_name=_('eigenaar'),
        help_text=_('Of deze werknemer een eigenaar is.')
    )

    class Meta:
        verbose_name = _('werknemer')
        verbose_name_plural = _('werknemers')

    def __str__(self):
        return self.name


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('werknemer'),
        help_text=_('Werknemer.')
    )

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE

    class Meta:
        verbose_name = _('werknemerstoken')
        verbose_name_plural = _('werknemerstokens')
