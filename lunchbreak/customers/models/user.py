
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django_sms.exceptions import PinTimeout
from django_sms.models import Phone
from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status
from rest_framework.response import Response

from ..exceptions import UserDisabled
from ..managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = [
        'name',
    ]

    class Meta:
        verbose_name = _('gebruiker')
        verbose_name_plural = _('gebruikers')

    def __str__(self):
        if self.name:
            return self.name
        return str(self.phone)

    objects = UserManager()

    phone = models.OneToOneField(
        'django_sms.Phone',
        on_delete=models.CASCADE,
        verbose_name=_('telefoonnummer'),
        help_text=_('Telefoonnummer.')
    )
    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('e-mailadres'),
        help_text=_('E-mailadres.')
    )

    enabled = models.BooleanField(
        default=True,
        verbose_name=_('ingeschakeld'),
        help_text=_('Ingeschakeld.')
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Lunchbreak werknemer'),
        help_text=_(
            'Lunchbreak werknemer, dit geeft toegang tot het controle paneel.'
        )
    )

    paymentlinks = models.ManyToManyField(
        'lunch.Store',
        through='PaymentLink',
        through_fields=(
            'user',
            'store',
        ),
        blank=True,
        verbose_name=_('getekende mandaten'),
        help_text=_('Getekende mandaten.')
    )

    @property
    def phonenumber(self):
        return self.phone.phone

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def notify(self, message, **kwargs):
        kwargs.setdefault('sound', 'default')

        self.tokens.all().send_message(
            message,
            **kwargs
        )

    def clean(self):
        """AbstractUser's clean method normalise the username which results in
        normalising the Phone instance here resulting in an error."""
        pass

    @staticmethod
    def register(phone):
        try:
            user = User.objects.get(
                phone__phone=phone
            )

            if not user.enabled:
                raise UserDisabled()

            if not settings.DEBUG:
                try:
                    user.phone.send_pin()
                except PinTimeout:
                    pass
            else:
                user.phone.reset_pin()

            if user.name:
                return Response(
                    status=status.HTTP_200_OK
                )
            return Response(
                status=status.HTTP_201_CREATED
            )
        except User.DoesNotExist:
            if not settings.DEBUG:
                phone, created = Phone.register(
                    phone=phone
                )
            else:
                phone = Phone.objects.create(
                    phone=phone
                )
            User.objects.get_or_create(
                phone=phone
            )

            return Response(
                status=status.HTTP_201_CREATED
            )

    @staticmethod
    def login(phone, pin, name, token):
        user = get_object_or_404(
            User,
            phone__phone=phone
        )

        if not user.enabled:
            raise UserDisabled()

        if name:
            user.name = name
        elif not user.name:
            raise LunchbreakException()

        if name:
            user.name = name
            user.save()

        if settings.DEBUG or user.phone.is_valid(pin=pin):
            return user
