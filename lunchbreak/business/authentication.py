from business.exceptions import IncorrectPassword, InvalidEmail
from business.models import Employee, EmployeeToken, Staff, StaffToken
from business.serializers import (EmployeePasswordRequestSerializer,
                                  EmployeeTokenSerializer,
                                  StaffPasswordRequestSerializer,
                                  StaffTokenSerializer)
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


class BusinessAuthentication(TokenAuthentication):

    @classmethod
    def login(cls, request):
        modelTokenSerializer = cls.TOKEN_SERIALIZER(data=request.data)
        if not modelTokenSerializer.is_valid():
            return BadRequest(modelTokenSerializer.errors)

        rawPassword = request.data['password']
        modelId = request.data[cls.MODEL_NAME]
        device = request.data['device']
        registrationId = request.data.get('registration_id', '')
        service = request.data.get('service', SERVICE_INACTIVE)
        device = request.data['device']

        try:
            model = cls.MODEL.objects.get(id=modelId)
        except cls.MODEL.DoesNotExist:
            return DoesNotExist(
                '{modelName} does not exist.'.format(
                    modelName=cls.MODEL_NAME.capitalize()
                )
            )

        if model.checkPassword(rawPassword):
            token, created = cls.TOKEN_MODEL.objects.create_token(
                arguments={
                    cls.MODEL_NAME: model,
                    'device': device
                },
                defaults={
                    'registration_id': registrationId,
                    'service': service
                },
                clone=True
            )
            tokenSerializer = cls.TOKEN_SERIALIZER(token)
            return Response(
                tokenSerializer.data,
                status=(
                    status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            )
        return IncorrectPassword().getResponse()

    @classmethod
    def requestPasswordReset(cls, request):
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
                return InvalidEmail().getResponse()
            except cls.MODEL.DoesNotExist:
                return InvalidEmail('Email address not found.').getResponse()

        model.passwordReset = random_token()
        model.save()

        subject = 'Lunchbreak wachtwoord herstellen'

        url = 'lunchbreakstore://reset/{model}/{email}/{passwordReset}'.format(
            model=cls.MODEL_NAME,
            email=to_email,
            passwordReset=model.passwordReset
        )

        templateArguments = {
            'name': model.name,
            'url': url
        }
        plaintext = render_to_string('requestReset.txt', templateArguments)
        html = render_to_string('requestReset.html', templateArguments)

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
