from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.functional import cached_property
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import BaseToken, Store


class PasswordModel(models.Model):
    password = models.CharField(max_length=255)
    passwordReset = models.CharField(max_length=TOKEN_IDENTIFIER_LENGTH, null=True, default=None)

    class Meta:
        abstract = True

    def setPassword(self, rawPassword):
        self.password = make_password(rawPassword)

    def checkPassword(self, rawPassword):
        return check_password(rawPassword, self.password)


class Staff(PasswordModel):
    store = models.ForeignKey(Store)
    email = models.EmailField(max_length=255)

    class Meta:
        verbose_name_plural = 'Staff'

    @cached_property
    def name(self):
        return self.store.name

    def __unicode__(self):
        return self.store.name


class StaffToken(BaseToken):
    staff = models.ForeignKey(Staff)


class Employee(PasswordModel):
    name = models.CharField(max_length=255)
    staff = models.ForeignKey(Staff)
    owner = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(Employee)
