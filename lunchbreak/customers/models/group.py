import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from lunch.config import TOKEN_IDENTIFIER_LENGTH, random_token
from Lunchbreak.fields import RoundingDecimalField

from ..managers import GroupManager
from ..tasks import send_group_created_emails


class Group(models.Model):

    class Meta:
        verbose_name = _('groep')
        verbose_name_plural = _('groepen')

    def __str__(self):
        return self.name

    objects = GroupManager()

    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    description = models.TextField(
        blank=True
    )
    store = models.ForeignKey(
        'lunch.Store',
        related_name='groups',
        verbose_name=_('winkel'),
        help_text=_('Winkel verbonden met deze groep.'),
    )
    email = models.EmailField(
        verbose_name=_('e-mailadres'),
        help_text=_('E-mailadres gebruikt voor informatie naartoe te sturen.')
    )

    delivery = models.BooleanField(
        default=False,
        verbose_name=_('levering'),
        help_text=_('Bestellingen worden geleverd.')
    )
    payment_online_only = models.BooleanField(
        default=False,
        verbose_name=_('enkel online betalen'),
        help_text=_('Enkel online betalingen zijn toegestaan.')
    )
    deadline = models.TimeField(
        default=datetime.time(hour=12),
        verbose_name=_('deadline bestelling'),
        help_text=_('Deadline voor het plaatsen van bestellingen elke dag.')
    )
    delay = models.DurationField(
        default=datetime.timedelta(minutes=30),
        verbose_name=_('geschatte vertraging'),
        help_text=_('Geschatte vertraging na plaatsen bestelling.')
    )
    discount = RoundingDecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        verbose_name=_('korting'),
        help_text=_('Korting bij het plaatsen van een bestelling.')
    )
    members = models.ManyToManyField(
        'User',
        blank=True,
        related_name='store_groups',
        verbose_name=_('leden'),
        help_text=_('Groepsleden.'),
    )
    admin_token = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        default=random_token
    )
    join_token = models.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        default=random_token
    )

    @property
    def receipt_time(self):
        return (
            datetime.datetime.combine(
                timezone.now(), self.deadline
            ) + self.delay
        ).time()

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        if created:
            send_group_created_emails.delay(
                group_id=instance.id
            )
