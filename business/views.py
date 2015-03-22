from business.authentication import EmployeeAuthentication, StaffAuthentication
from business.models import Employee, Staff
from business.responses import InvalidEmail
from business.serializers import (EmployeeSerializer, OrderSerializer,
                                  ShortFoodSerializer,
                                  ShortIngredientGroupSerializer,
                                  ShortOrderSerializer, StaffSerializer)
from customers.models import (Order, ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED,
                              ORDER_STATUS_STARTED, ORDER_STATUS_WAITING)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from lunch.models import (DefaultFood, DefaultIngredient, Food, FoodCategory,
                          FoodType, Ingredient, IngredientGroup, Store)
from lunch.responses import BadRequest, DoesNotExist
from lunch.serializers import (DefaultFoodCategorySerializer,
                               DefaultFoodSerializer,
                               DefaultIngredientSerializer, FoodTypeSerializer)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


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


class EmployeeRequestResetView(APIView):
    '''
    Send a password reset mail to an employee.
    '''

    authentication_classes = (StaffAuthentication,)

    def get(self, request, employee_id, format=None):
        staff = request.user
        try:
            employee = Employee.objects.get(id=employee_id, staff=staff)
        except ObjectDoesNotExist:
            return DoesNotExist()
        return EmployeeAuthentication.requestPasswordReset(request, staff.email, employee)


class FoodListView(generics.ListAPIView):
    '''
    List the food.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortFoodSerializer
    queryset = Food.objects.all()


class DefaultFoodListView(FoodListView):
    pagination_class = None
    queryset = DefaultFood.objects.all()


class FoodRetrieveView(generics.RetrieveAPIView):
    '''
    Retrieve a (default) food.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = DefaultFoodSerializer  # Default serializer doesn't return the store
    queryset = Food.objects.all()


class DefaultFoodRetrieveView(FoodRetrieveView):
    queryset = DefaultFood.objects.all()


class IngredientListView(generics.ListAPIView):
    '''
    List the food ingredients.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = DefaultIngredientSerializer

    def get_queryset(self):
        return Ingredient.objects.filter(store_id=self.request.user.staff.store_id)


class DefaultIngredientListView(IngredientListView):
    pagination_class = None

    def get_queryset(self):
        return DefaultIngredient.objects.all()


class FoodCategoryListView(generics.ListAPIView):
    '''
    List the food categories.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = DefaultFoodCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return FoodCategory.objects.filter(store_id=self.request.user.staff.store_id)


class FoodTypeListView(generics.ListAPIView):
    '''
    List the food types.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = FoodTypeSerializer
    pagination_class = None

    def get_queryset(self):
        return FoodType.objects.all()


class IngredientGroupListView(generics.ListAPIView):
    '''
    List the ingredient groups.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortIngredientGroupSerializer
    pagination_class = None

    def get_queryset(self):
        return IngredientGroup.objects.all()


class OrderListView(generics.ListAPIView):
    '''
    List the store's orders.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortOrderSerializer

    def get_queryset(self):
        result = Order.objects.filter(store_id=self.request.user.staff.store_id, status__in=[ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED, ORDER_STATUS_WAITING])
        if self.request.method == 'GET':
            if 'option' in self.kwargs and self.kwargs['option'] == 'pickupTime':
                return result.order_by('pickupTime')
            return result.order_by('-orderedTime')
        return result


class OrderUpdateView(generics.RetrieveUpdateAPIView):
    '''
    Update the status of an order and receive specific information about an order.
    '''

    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(store_id=self.request.user.staff.store_id, status__in=[ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED, ORDER_STATUS_WAITING])


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


class StaffRequestResetView(APIView):
    '''
    Send password reset mail.
    '''

    def get(self, request, email, format=None):
        return StaffAuthentication.requestPasswordReset(request, email)


class StaffResetView(APIView):
    '''
    Reset password.
    '''

    def post(self, request, email, passwordReset, format=None):
        try:
            validate_email(email)
            staff = Staff.objects.get(email=email)
        except ValidationError:
            return InvalidEmail()
        except ObjectDoesNotExist:
            return InvalidEmail('Email address not found.')

        if staff.passwordReset is None or 'password' not in request.data:
            return BadRequest()
        elif staff.passwordReset != passwordReset:
            staff.passwordReset = None
            staff.save()
            return BadRequest()
        else:
            staff.passwordReset = None
            staff.setPassword(request.data['password'])
            staff.save()
            return Response(status=status.HTTP_200_OK)
