from django.db import models
from django.utils.translation import ugettext as _
from lunch.models import BaseToken
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import status
from rest_framework.response import Response


class UserToken(BaseToken):

    class Meta:
        verbose_name = _('gebruikerstoken')
        verbose_name_plural = _('gebruikerstokens')

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )

    @staticmethod
    def response(user, device, service=SERVICE_INACTIVE, registration_id=''):
        from ..serializers import UserTokenDetailSerializer

        token, created = UserToken.objects.create_token(
            arguments={
                'user': user,
                'device': device
            },
            defaults={
                'registration_id': registration_id,
                'service': service
            },
            clone=True
        )
        serializer = UserTokenDetailSerializer(token)
        return Response(
            serializer.data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        )
