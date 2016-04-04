from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from lunch.authentication import TokenAuthentication
from lunch.config import random_token
from lunch.responses import BadRequest, DoesNotExist
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import status
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
        if not serializer_model_token.is_valid():
            return BadRequest(serializer_model_token.errors)

        password_raw = request.data['password']
        model_id = request.data[cls.MODEL_NAME]
        device = request.data['device']
        registration_id = request.data.get('registration_id', '')
        service = request.data.get('service', SERVICE_INACTIVE)
        device = request.data['device']

        try:
            model = cls.MODEL.objects.get(id=model_id)
        except cls.MODEL.DoesNotExist:
            return DoesNotExist(
                '{model_name} does not exist.'.format(
                    model_name=cls.MODEL_NAME.capitalize()
                )
            )

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
    def password_reset_request(cls, request):
        serializer = cls.REQUEST_SERIALIZER(data=request.data)
        if not serializer.is_valid():
            return BadRequest(serializer.errors)

        if cls.MODEL_NAME == 'employee':
            try:
                model = cls.MODEL.objects.get(id=request.data['id'])
                to_email = model.staff.email
            except cls.MODEL.DoesNotExist:
                return DoesNotExist()
        else:
            to_email = request.data['email']

            try:
                validate_email(to_email)
                model = cls.MODEL.objects.get(email=to_email)
            except ValidationError:
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
    TOKEN_MODEL = StaffToken
    TOKEN_SERIALIZER = StaffTokenSerializer
    REQUEST_SERIALIZER = StaffPasswordRequestSerializer


class EmployeeAuthentication(BusinessAuthentication):
    MODEL = Employee
    MODEL_NAME = 'employee'
    TOKEN_MODEL = EmployeeToken
    TOKEN_SERIALIZER = EmployeeTokenSerializer
    REQUEST_SERIALIZER = EmployeePasswordRequestSerializer
