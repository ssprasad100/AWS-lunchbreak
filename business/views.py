from business.authentication import StaffAuthentication
from business.exceptions import IncorrectPassword, InvalidEmail
from business.models import Employee, Staff, StaffToken
from business.serializers import (EmployeeSerializer, StaffSerializer,
                                  StaffTokenSerializer)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import BadHeaderError, send_mail
from django.core.validators import validate_email
from lunch.exceptions import BadRequest, DoesNotExist
from lunch.models import Store, tokenGenerator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


class StaffListView(generics.ListAPIView):
    '''
    List the staff.
    '''

    serializer_class = StaffSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            stores = Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
            return Staff.objects.filter(store__in=stores)
        if 'id' in self.kwargs:
            return Staff.objects.filter(id=self.kwargs['id'])
        return Staff.objects.all()

    def post(self, request, format=None):
        if 'password' not in request.data or 'staffId' not in request.data or 'device' not in request.data:
            raise BadRequest()

        rawPassword = request.data['password']
        staffId = request.data['staffId']
        device = request.data['device']

        try:
            staff = Staff.objects.get(id=staffId)
        except ObjectDoesNotExist:
            raise DoesNotExist('Staff does not exist.')

        if staff.checkPassword(rawPassword):
            token, created = StaffToken.objects.get_or_create(device=device, staff=staff)
            if not created:
                token.identifier = tokenGenerator()
            token.save()
            tokenSerializer = StaffTokenSerializer(token)
            data = dict(tokenSerializer.data)
            return Response(data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))
        raise IncorrectPassword()


class StaffRequestReset(APIView):
    '''
    Send password reset mail.
    '''

    def get(self, request, email, format=None):
        try:
            validate_email(email)
        except ValidationError:
            raise InvalidEmail()

        try:
            staff = Staff.objects.get(email=email)
        except ObjectDoesNotExist:
            raise InvalidEmail('Email address not found.')

        staff.passwordReset = tokenGenerator()
        staff.save()
        url = 'http://api.lunchbreakapp.be/v1/business/reset/%s/%s' % (email, staff.passwordReset,)

        message = '''A password reset has been requested for this staff account.

Please visit %s or ignore this email if you did not request this.
        ''' % url
        try:
            send_mail('Lunchbreak password reset', message, 'hello@cloock.be', [email], fail_silently=False)
        except BadHeaderError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class StaffResetView(APIView):
    '''
    Reset password.
    '''
    def post(self, request, email, passwordReset, format=None):
        try:
            validate_email(email)
            staff = Staff.objects.get(email=email)
        except ValidationError:
            raise InvalidEmail()
        except ObjectDoesNotExist:
            raise InvalidEmail('Email address not found.')

        if staff.passwordReset is None or 'password' not in request.data:
            raise BadRequest()
        elif staff.passwordReset != passwordReset:
            staff.passwordReset = None
            staff.save()
            raise BadRequest()
        else:
            staff.passwordReset = None
            staff.setPassword(request.data['password'])
            staff.save()
            return Response(status=status.HTTP_200_OK)


class EmployeeListView(generics.ListAPIView):
    '''
    List the employees.
    '''

    authentication_classes = (StaffAuthentication,)
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Employee.objects.filter(id=self.kwargs['id'], staff=self.request.user)
        return Employee.objects.filter(staff=self.request.user)
