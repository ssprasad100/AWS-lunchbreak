from business.authentication import EmployeeAuthentication, StaffAuthentication
from business.exceptions import InvalidEmail
from business.models import Employee, Staff
from business.serializers import (EmployeeSerializer, OrderSerializer,
                                  StaffSerializer)
from customers.models import (Order, ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED,
                              ORDER_STATUS_STARTED, ORDER_STATUS_WAITING)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import BadHeaderError, send_mail
from django.core.validators import validate_email
from lunch.exceptions import BadRequest
from lunch.models import Store, tokenGenerator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


class StaffView(generics.ListAPIView):
    '''
    List the staff and login.
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
        return StaffAuthentication.login(request)


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
            send_mail('Lunchbreak password reset', message, 'noreply@lunchbreakapp.be', [email], fail_silently=False)
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


class EmployeeView(generics.ListAPIView):
    '''
    List the employees and login.
    '''

    authentication_classes = (StaffAuthentication,)
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Employee.objects.filter(id=self.kwargs['id'], staff=self.request.user)
        return Employee.objects.filter(staff=self.request.user)

    def post(self, request, format=None):
        return EmployeeAuthentication.login(request)


class OrderListView(generics.ListAPIView):
    '''
    List the store's orders.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(store_id=self.request.user.staff.store_id, status__in=[ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED, ORDER_STATUS_WAITING])


class OrderUpdateView(generics.UpdateAPIView):
    '''
    Update the status of an order.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(store_id=self.request.user.staff.store_id, status__in=[ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED, ORDER_STATUS_WAITING])
