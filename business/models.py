from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from lunch.models import Store, BaseToken


class Staff(models.Model):
    store = models.ForeignKey(Store)
    password = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'Staff'

    def setPassword(self, rawPassword):
        self.password = make_password(rawPassword)

    def checkPassword(self, rawPassword):
        return check_password(rawPassword, self.password)


class StaffToken(BaseToken):
    staff = models.ForeignKey(Staff)


class Employee(models.Model):
    name = models.CharField(max_length=128)
    staff = models.ForeignKey(Staff)
    pin = models.CharField(max_length=128)

    def setPin(self, rawPin):
        self.pin = make_password(rawPin)

    def checkPin(self, rawPin):
        return check_password(rawPin, self.pin)


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(Employee)
