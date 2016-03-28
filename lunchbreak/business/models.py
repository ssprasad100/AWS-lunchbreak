from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import BaseToken


class AbstractPasswordReset(models.Model):
    password_reset = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        null=True,
        default=None
    )

    class Meta:
        abstract = True


class AbstractPassword(AbstractPasswordReset):
    password = models.CharField(
        max_length=255
    )

    class Meta:
        abstract = True

    def set_password(self, password_raw):
        self.password = make_password(password_raw)

    def check_password(self, password_raw):
        return check_password(password_raw, self.password)


class StaffManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not password:
            raise ValueError('A password is required for staff.')

        email = self.normalize_email(email)
        staff = self.model(
            email=email
        )
        staff.set_password(password)
        staff.save()
        return staff

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password
        )
        user.is_superuser = True
        user.save()
        return user


class Staff(AbstractBaseUser, AbstractPasswordReset):
    store = models.OneToOneField(
        'lunch.Store',
        on_delete=models.CASCADE,
        null=True
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text=_('Email address')
    )
    first_name = models.CharField(
        max_length=255,
        help_text=_('First name')
    )
    last_name = models.CharField(
        max_length=255,
        help_text=_('Last name')
    )
    merchant = models.ForeignKey(
        'django_gocardless.Merchant',
        on_delete=models.SET_NULL,
        null=True
    )

    is_superuser = models.BooleanField(
        default=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name'
    ]

    objects = StaffManager()

    @cached_property
    def name(self):
        return self.get_full_name()

    @cached_property
    def is_staff(self):
        return self.is_superuser

    @cached_property
    def is_active(self):
        return True

    @property
    def is_merchant(self):
        return self.merchant is not None and self.merchant.organisation_id

    def get_full_name(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name
        )

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    class Meta:
        verbose_name_plural = 'Staff'

    def __unicode__(self):
        return self.name


class StaffToken(BaseToken):
    staff = models.ForeignKey(Staff)

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

    def __unicode__(self):
        return self.name


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(Employee)

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE
