from business.exceptions import IncorrectPassword
from business.models import Employee, EmployeeToken, Staff, StaffToken
from business.serializers import EmployeeTokenSerializer, StaffTokenSerializer
from django.core.exceptions import ObjectDoesNotExist
from lunch.authentication import TokenAuthentication
from lunch.exceptions import DoesNotExist, BadRequest
from lunch.models import tokenGenerator
from rest_framework import status
from rest_framework.response import Response


class BusinessAuthentication(TokenAuthentication):

    @classmethod
    def login(cls, request):
        modelTokenSerializer = cls.TOKEN_SERIALIZER(data=request.data)
        if not modelTokenSerializer.is_valid():
            raise BadRequest(modelTokenSerializer.errors)

        rawPassword = request.data['password']
        modelId = request.data[cls.FOREIGN_KEY_ATTRIBUTE]
        device = request.data['device']

        try:
            model = cls.MODEL.objects.get(id=modelId)
        except ObjectDoesNotExist:
            raise DoesNotExist('%s does not exist.' % cls.FOREIGN_KEY_ATTRIBUTE.capitalize())

        if model.checkPassword(rawPassword):
            arguments = {'device': device, cls.FOREIGN_KEY_ATTRIBUTE: model}
            token, created = cls.FOREIGN_KEY_TOKEN.objects.get_or_create(**arguments)
            if not created:
                token.identifier = tokenGenerator()
            token.save()
            tokenSerializer = cls.TOKEN_SERIALIZER(token)
            return Response(tokenSerializer.data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))
        raise IncorrectPassword()


class StaffAuthentication(BusinessAuthentication):
    FOREIGN_KEY_ATTRIBUTE = 'staff'
    FOREIGN_KEY_TOKEN = StaffToken
    TOKEN_SERIALIZER = StaffTokenSerializer
    MODEL = Staff


class EmployeeAuthentication(BusinessAuthentication):
    FOREIGN_KEY_ATTRIBUTE = 'employee'
    FOREIGN_KEY_TOKEN = EmployeeToken
    TOKEN_SERIALIZER = EmployeeTokenSerializer
    MODEL = Employee
