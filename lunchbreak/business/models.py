from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.functional import cached_property
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import BaseToken, Store


class PasswordModel(models.Model):
    password = models.CharField(
        max_length=255
    )
    password_reset = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        null=True,
        default=None
    )

    class Meta:
        abstract = True

    def set_password(self, password_raw):
        self.password = make_password(password_raw)

    def check_password(self, password_raw):
        return check_password(password_raw, self.password)


class Staff(PasswordModel):
    store = models.ForeignKey(Store)
    email = models.EmailField(
        max_length=255,
        unique=True
    )

    class Meta:
        verbose_name_plural = 'Staff'

    @cached_property
    def name(self):
        return self.store.name

    def __unicode__(self):
        return self.name


class StaffToken(BaseToken):
    staff = models.ForeignKey(Staff)

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE


class Employee(PasswordModel):
    name = models.CharField(
        max_length=255
    )
    staff = models.ForeignKey(Staff)
    owner = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return self.name


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(Employee)

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE
