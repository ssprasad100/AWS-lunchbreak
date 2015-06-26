from business.authentication import EmployeeAuthentication, StaffAuthentication
from business.exceptions import InvalidDatetime
from business.models import Employee, Staff
from business.permissions import StoreOwnerPermission
from business.responses import InvalidEmail
from business.serializers import (EmployeeSerializer, FoodCategorySerializer,
                                  IngredientGroupSerializer,
                                  IngredientSerializer, OrderSerializer,
                                  ShortFoodSerializer,
                                  ShortIngredientGroupSerializer,
                                  ShortOrderSerializer, StaffSerializer,
                                  StoreFoodSerializer, StoreSerializer)
from customers.models import (ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED,
                              ORDER_STATUS_STARTED, ORDER_STATUS_WAITING,
                              Order)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from lunch.models import (DefaultFood, DefaultIngredient,
                          DefaultIngredientGroup, Food, FoodCategory, FoodType,
                          Ingredient, IngredientGroup, Store)
from lunch.responses import BadRequest, DoesNotExist
from lunch.serializers import (FoodTypeSerializer, HolidayPeriodSerializer,
                               OpeningHoursSerializer)
from lunch.views import (StoreCategoryListViewBase, getHolidayPeriods,
                         getOpeningAndHoliday, getOpeningHours)
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

AVAILABLE_STATUSES = [ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED, ORDER_STATUS_WAITING]


def getSince(request, kwargs, methodCheck=False):
    if (methodCheck or request.method == 'GET') and 'datetime' in kwargs and kwargs['datetime'] is not None:
        sinceString = kwargs['datetime']
        try:
            return timezone.datetime.strptime(sinceString, '%d-%m-%Y-%H-%M-%S')
        except ValueError:
            raise InvalidDatetime()
    return None


class ListCreateStoreView(generics.ListCreateAPIView):

    def perform_create(self, serializer):
        store = self.request.user.staff.store if isinstance(self.request.user, Employee) else self.request.user.store
        serializer.save(store=store)


class StoreSingleView(generics.RetrieveUpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = StoreSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def get_queryset(self):
        return Store.objects.filter(id=self.request.user.staff.store_id)


class EmployeeView(generics.ListAPIView):
    authentication_classes = (StaffAuthentication,)
    serializer_class = EmployeeSerializer
    pagination_class = None

    def get_queryset(self):
        return Employee.objects.filter(staff=self.request.user)

    def post(self, request, format=None):
        return EmployeeAuthentication.login(request)


class EmployeeRequestResetView(APIView):
    authentication_classes = (StaffAuthentication,)

    def get(self, request, employee_id, format=None):
        staff = request.user
        try:
            employee = Employee.objects.get(id=employee_id, staff=staff)
        except ObjectDoesNotExist:
            return DoesNotExist()
        return EmployeeAuthentication.requestPasswordReset(request, staff.email, employee)


class FoodListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortFoodSerializer

    def get_queryset(self):
        result = Food.objects.filter(store=self.request.user.staff.store)
        since = getSince(self.request, self.kwargs)
        if since is not None:
            return result.filter(lastModified__gte=since)
        return result


class FoodView(FoodListView, generics.CreateAPIView):
    permission_classes = (StoreOwnerPermission,)

    def post(self, request, format=None, datetime=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(store=request.user.staff.store)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return BadRequest()


class DefaultFoodListView(FoodListView):
    pagination_class = None
    queryset = DefaultFood.objects.all()


class FoodSingleView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (StoreOwnerPermission,)
    authentication_classes = (EmployeeAuthentication,)

    def get_queryset(self, *args, **kwargs):
        return Food.objects.filter(store=self.request.user.staff.store)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return StoreFoodSerializer
        else:
            return ShortFoodSerializer


class DefaultFoodSingleView(generics.RetrieveAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = StoreFoodSerializer
    permission_classes = (StoreOwnerPermission,)
    queryset = DefaultFood.objects.all()


class IngredientMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        result = Ingredient.objects.filter(store=self.request.user.staff.store)
        since = getSince(self.request, self.kwargs)
        if since is not None:
            return result.filter(lastModified__gte=since)
        return result


class IngredientSingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        result = Ingredient.objects.filter(store=self.request.user.staff.store)
        since = getSince(self.request, self.kwargs)
        if since is not None:
            return result.filter(lastModified__gte=since)
        return result


class DefaultIngredientListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = DefaultIngredient.objects.all()


class FoodCategoryMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = FoodCategorySerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return FoodCategory.objects.filter(store=self.request.user.staff.store)


class FoodCategorySingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = FoodCategorySerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        return FoodCategory.objects.filter(store=self.request.user.staff.store)


class FoodTypeListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = FoodTypeSerializer
    pagination_class = None
    queryset = FoodType.objects.all()


class IngredientGroupMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortIngredientGroupSerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return IngredientGroup.objects.filter(store=self.request.user.staff.store)


class IngredientGroupSingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientGroupSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        return IngredientGroup.objects.filter(store=self.request.user.staff.store)


class DefaultIngredientGroupMultiView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientGroupSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = DefaultIngredientGroup.objects.all()
        if 'foodType' in self.kwargs and self.kwargs['foodType'] is not None:
            return queryset.filter(foodType_id=self.kwargs['foodType'])
        return queryset


class OrderListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortOrderSerializer

    def get_queryset(self):
        result = Order.objects.filter(store=self.request.user.staff.store, status__in=AVAILABLE_STATUSES)
        if self.request.method == 'GET':
            since = getSince(self.request, self.kwargs, methodCheck=True)

            if 'option' in self.kwargs and self.kwargs['option'] == 'pickupTime':
                result = result.order_by('pickupTime')
                if since is not None:
                    result = result.filter(pickupTime__gt=since)
            else:
                result = result.order_by('-orderedTime')
                if since is not None:
                    result = result.filter(orderedTime__gt=since)
        return result


class OrderUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(store=self.request.user.staff.store, status__in=AVAILABLE_STATUSES)


class StaffMultiView(generics.ListAPIView):
    serializer_class = StaffSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            stores = Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
            return Staff.objects.filter(store__in=stores)
        elif self.request.method != 'GET':
            return Staff.objects.all()
        raise MethodNotAllowed(self.request.method)

    def post(self, request, format=None):
        return StaffAuthentication.login(request)


class StaffSingleView(generics.RetrieveAPIView):
    authentication_classes = (StaffAuthentication,)
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()

    def get_queryset(self):
        return Staff.objects.filter(id=self.request.user.id)


class StaffRequestResetView(APIView):
    def get(self, request, email, format=None):
        return StaffAuthentication.requestPasswordReset(request, email)


class StaffResetView(APIView):
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


class StoreOpenView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OpeningHoursSerializer
    pagination_class = None
    queryset = None

    def get(self, request, *args, **kwargs):
        return getOpeningAndHoliday(self.request.user.staff.store_id)


class StoreCategoryListView(StoreCategoryListViewBase):
    authentication_classes = (EmployeeAuthentication,)


class OpeningHoursListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OpeningHoursSerializer
    pagination_class = None

    def get_queryset(self):
        return getOpeningHours(self.request.user.staff.store_id)


class HolidayPeriodListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = HolidayPeriodSerializer
    pagination_class = None

    def get_queryset(self):
        return getHolidayPeriods(self.request.user.staff.store_id)
