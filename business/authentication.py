from business.models import Employee, EmployeeToken, Staff, StaffToken
from business.responses import IncorrectPassword, InvalidEmail
from business.serializers import EmployeeTokenSerializer, StaffTokenSerializer
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from lunch.authentication import TokenAuthentication
from lunch.models import tokenGenerator
from lunch.responses import BadRequest, DoesNotExist
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
        nameKey = 'name' if request.version > 2 else 'device'
        name = request.data[nameKey]

        try:
            model = cls.MODEL.objects.get(id=modelId)
        except ObjectDoesNotExist:
            return DoesNotExist('%s does not exist.' % cls.MODEL_NAME.capitalize())

        if model.checkPassword(rawPassword):
            arguments = {'name': name, cls.MODEL_NAME: model}
            token, created = cls.TOKEN_MODEL.objects.get_or_create(**arguments)
            if not created:
                token.identifier = tokenGenerator()
            token.save()
            tokenSerializer = cls.TOKEN_SERIALIZER(token)
            return Response(tokenSerializer.data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))
        return IncorrectPassword()

    @classmethod
    def requestPasswordReset(cls, request, to_email=None, model=None):
        if to_email is not None and model is None:
            try:
                validate_email(to_email)
            except ValidationError:
                return InvalidEmail()

            try:
                model = cls.MODEL.objects.get(email=to_email)
            except ObjectDoesNotExist:
                return InvalidEmail('Email address not found.')
        elif model is None:
            return BadRequest()

        model.passwordReset = tokenGenerator()
        model.save()
        subject, from_email = 'Lunchbreak password reset', settings.EMAIL_FROM
        url = 'http://%s/v1/business/reset/%s/%s/%s' % (settings.HOST, cls.MODEL_NAME, to_email, model.passwordReset,)

        templateArguments = {
            'name': model.name,
            'url': url
        }
        plaintext = render_to_string('requestReset.txt', templateArguments)
        html = render_to_string('requestReset.html', templateArguments)

        msg = EmailMultiAlternatives(subject, plaintext, from_email, [to_email])
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


class EmployeeAuthentication(BusinessAuthentication):
    MODEL = Employee
    MODEL_NAME = 'employee'
    TOKEN_MODEL = EmployeeToken
    TOKEN_SERIALIZER = EmployeeTokenSerializer
