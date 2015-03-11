from business.models import Employee, EmployeeToken, Staff, StaffToken
from business.responses import IncorrectPassword
from business.serializers import EmployeeTokenSerializer, StaffTokenSerializer
from django.core.exceptions import ObjectDoesNotExist
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
        device = request.data['device']

        try:
            model = cls.MODEL.objects.get(id=modelId)
        except ObjectDoesNotExist:
            return DoesNotExist('%s does not exist.' % cls.MODEL_NAME.capitalize())

        if model.checkPassword(rawPassword):
            arguments = {'device': device, cls.MODEL_NAME: model}
            token, created = cls.TOKEN_MODEL.objects.get_or_create(**arguments)
            if not created:
                token.identifier = tokenGenerator()
            token.save()
            tokenSerializer = cls.TOKEN_SERIALIZER(token)
            return Response(tokenSerializer.data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))
        return IncorrectPassword()


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
