from django.conf import settings
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from lunch.authentication import TokenAuthentication
from lunch.config import random_token
from Lunchbreak.exceptions import LunchbreakException
from push_notifications.models import BareDevice
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .exceptions import IncorrectPassword, InvalidEmail
from .models import Employee, EmployeeToken, Staff, StaffToken
from .serializers import (EmployeePasswordRequestSerializer,
                          EmployeeTokenSerializer,
                          StaffPasswordRequestSerializer, StaffTokenSerializer)


class BusinessAuthentication(TokenAuthentication):

    @classmethod
    def login(cls, request):
        serializer_model_token = cls.TOKEN_SERIALIZER(data=request.data)
        serializer_model_token.is_valid(raise_exception=True)

        password_raw = request.data['password']
        device = request.data['device']
        registration_id = request.data.get('registration_id', '')
        service = request.data.get('service', BareDevice.INACTIVE)
        device = request.data['device']

        model = cls.get_model(request.data)

        if model.check_password(password_raw):
            token, created = cls.TOKEN_MODEL.objects.create_token(
                arguments={
                    cls.MODEL_NAME: model,
                    'device': device
                },
                defaults={
                    'registration_id': registration_id,
                    'service': service
                },
                clone=True
            )
            serializer_token = cls.TOKEN_SERIALIZER(token)
            return Response(
                serializer_token.data,
                status=(
                    status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            )
        return IncorrectPassword().response

    @classmethod
    def get_model(cls, data):
        model_id = data[cls.SERIALIZER_FIELD]
        return get_object_or_404(
            cls.MODEL,
            **{
                cls.MODEL_FIELD: model_id
            }
        )

    @classmethod
    def password_reset_request(cls, request):
        serializer = cls.REQUEST_SERIALIZER(data=request.data)
        serializer.is_valid(raise_exception=True)

        if cls.MODEL_NAME == 'employee':
            model = cls.MODEL.objects.get(id=request.data['id'])
            to_email = model.staff.email
        else:
            to_email = request.data['email'].lower()

            try:
                validate_email(to_email)
                model = cls.MODEL.objects.get(email__iexact=to_email)
            except LunchbreakException:
                return InvalidEmail().response
            except cls.MODEL.DoesNotExist:
                return InvalidEmail('Email address not found.').response

        model.password_reset = random_token()
        model.save()

        subject = 'Lunchbreak wachtwoord herstellen'

        url = 'lunchbreakstore://reset/{model}/{email}/{password_reset}'.format(
            model=cls.MODEL_NAME,
            email=to_email,
            password_reset=model.password_reset
        )

        template_args = {
            'name': model.name,
            'url': url
        }
        plaintext = render_to_string('reset_request.txt', template_args)
        html = render_to_string('reset_request.html', template_args)

        msg = EmailMultiAlternatives(
            subject,
            plaintext,
            settings.EMAIL_FROM,
            [to_email]
        )
        msg.attach_alternative(html, 'text/html')

        try:
            msg.send()
        except BadHeaderError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)


class StaffAuthentication(BusinessAuthentication):
    MODEL = Staff
    MODEL_NAME = 'staff'
    MODEL_FIELD = 'email'
    SERIALIZER_FIELD = 'email'
    TOKEN_MODEL = StaffToken
    TOKEN_SERIALIZER = StaffTokenSerializer
    REQUEST_SERIALIZER = StaffPasswordRequestSerializer

    @classmethod
    def get_model(cls, data):
        if 'email' not in data and 'staff' not in data:
            raise ValidationError('Email or staff field is required.')

        uses_email = 'email' in data
        model_field = 'email__iexact' if uses_email else 'id'
        model_id = data['email'].lower() if uses_email else data['staff']
        return get_object_or_404(
            cls.MODEL,
            **{
                model_field: model_id
            }
        )


class EmployeeAuthentication(BusinessAuthentication):
    MODEL = Employee
    MODEL_NAME = 'employee'
    MODEL_FIELD = 'id'
    SERIALIZER_FIELD = 'employee'
    TOKEN_MODEL = EmployeeToken
    TOKEN_SERIALIZER = EmployeeTokenSerializer
    REQUEST_SERIALIZER = EmployeePasswordRequestSerializer
