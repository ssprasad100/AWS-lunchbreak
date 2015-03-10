from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from lunch.models import Store, BaseToken, IDENTIFIER_LENGTH


class PasswordModel(models.Model):
    password = models.CharField(max_length=128)
    passwordReset = models.CharField(max_length=IDENTIFIER_LENGTH, null=True, default=None)

    class Meta:
        abstract = True

    def setPassword(self, rawPassword):
        self.password = make_password(rawPassword)

    def checkPassword(self, rawPassword):
        return check_password(rawPassword, self.password)


class Staff(PasswordModel):
    store = models.ForeignKey(Store)
    email = models.EmailField(max_length=254)

    class Meta:
        verbose_name_plural = 'Staff'


class StaffToken(BaseToken):
    staff = models.ForeignKey(Staff)


class Employee(PasswordModel):
    name = models.CharField(max_length=128)
    staff = models.ForeignKey(Staff)
    owner = models.BooleanField(default=False)


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(Employee)
