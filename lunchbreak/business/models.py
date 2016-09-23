from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import BaseToken

from .managers import StaffManager


class AbstractPasswordReset(models.Model):
    password_reset = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name=_('Wachtwoord reset'),
        help_text=_('Code gebruikt om het wachtwoord te veranderen')
    )

    class Meta:
        abstract = True


class AbstractPassword(AbstractPasswordReset):
    password = models.CharField(
        max_length=255,
        verbose_name=_('Wachtwoord'),
        help_text=_('Geëncrypteerd wachtwoord')
    )

    class Meta:
        abstract = True

    def set_password(self, password_raw):
        self.password = make_password(password_raw)

    def check_password(self, password_raw):
        return check_password(password_raw, self.password)


class Staff(AbstractPassword):
    store = models.OneToOneField(
        'lunch.Store',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Winkel'),
        help_text=_('Winkel')
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name=_('E-mailadres'),
        help_text=_('E-mailadres')
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name=_('Voornaam'),
        help_text=_('Voornaam')
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name=_('Familienaam'),
        help_text=_('Familienaam')
    )
    merchant = models.ForeignKey(
        'django_gocardless.Merchant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_('GoCardless account')
    )

    objects = StaffManager()

    @cached_property
    def name(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name
        )

    @property
    def is_merchant(self):
        return self.merchant is not None and self.merchant.organisation_id

    class Meta:
        verbose_name = _('Personeel')
        verbose_name_plural = _('Personeel')

    def __str__(self):
        return '{store}: {name}'.format(
            store=self.store,
            name=self.name
        )


class StaffToken(BaseToken):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE


class Employee(AbstractPassword):
    name = models.CharField(
        max_length=255
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )
    owner = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE
