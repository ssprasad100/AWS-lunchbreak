from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .abstract_password_reset import AbstractPasswordReset


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
