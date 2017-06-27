from django.db import models
from django.utils.translation import ugettext_lazy as _
from lunch.config import TOKEN_IDENTIFIER_LENGTH


class AbstractPasswordReset(models.Model):
    password_reset = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name=_('wachtwoord reset'),
        help_text=_('Code gebruikt om het wachtwoord te veranderen.')
    )

    class Meta:
        abstract = True
