from business.authentication import EmployeeAuthentication, StaffAuthentication
from business.exceptions import (InvalidDatetime, InvalidEmail,
                                 InvalidPasswordReset)
from business.models import Employee, Staff
from business.permissions import StoreOwnerPermission
from business.serializers import (EmployeeSerializer,
                                  IngredientGroupSerializer,
                                  IngredientSerializer, OrderSerializer,
                                  ShortFoodSerializer,
                                  ShortIngredientGroupSerializer,
                                  ShortOrderSerializer, StaffSerializer,
                                  StoreSerializer)
from customers.config import (ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED,
                              ORDER_STATUS_STARTED, ORDER_STATUS_WAITING)
from customers.models import Order
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lunch.models import (Food, FoodCategory, FoodType, Ingredient,
                          IngredientGroup, Quantity, Store)
from lunch.responses import BadRequest, DoesNotExist
from lunch.serializers import (FoodTypeSerializer, HolidayPeriodSerializer,
                               OpeningHoursSerializer, QuantitySerializer,
                               ShortFoodCategorySerializer,
                               ShortSingleFoodSerializer)
from lunch.views import (StoreCategoryListViewBase, getHolidayPeriods,
                         getOpeningAndHoliday, getOpeningHours)
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView

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

    def post(self, request, *args, **kwargs):
        return EmployeeAuthentication.login(request)


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

    def post(self, request, datetime=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(store=request.user.staff.store)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return BadRequest()


class FoodSingleView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (StoreOwnerPermission,)
    authentication_classes = (EmployeeAuthentication,)

    def get_queryset(self, *args, **kwargs):
        return Food.objects.filter(store=self.request.user.staff.store)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return ShortSingleFoodSerializer
        else:
            return ShortFoodSerializer


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


class FoodCategoryMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortFoodCategorySerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return FoodCategory.objects.filter(store=self.request.user.staff.store)


class FoodCategorySingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortFoodCategorySerializer
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

    def post(self, request, *args, **kwargs):
        return StaffAuthentication.login(request)


class StaffSingleView(generics.RetrieveAPIView):
    authentication_classes = (StaffAuthentication,)
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()

    def get_queryset(self):
        return Staff.objects.filter(id=self.request.user.id)


class ResetRequestView(generics.CreateAPIView):

    def post(self, request, authentication, *args, **kwargs):
        return authentication.requestPasswordReset(request)


class PasswordResetView(generics.CreateAPIView):

    def post(self, request, model, tokenModel, serializerClass, employee=False, *args, **kwargs):
        passwordSerializer = serializerClass(data=request.data)
        if passwordSerializer.is_valid():
            email = request.data['email']
            passwordReset = request.data['passwordReset']

            try:
                validate_email(email)
                if employee:
                    m = model.objects.get(staff__email=email, passwordReset=passwordReset)
                else:
                    m = model.objects.get(email=email, passwordReset=passwordReset)
            except ValidationError:
                return InvalidEmail().getResponse()
            except model.DoesNotExist:
                return InvalidPasswordReset().getResponse()

            m.passwordReset = None
            m.setPassword(request.data['password'])
            m.save()

            tokenModel.objects.filter(**{model.__name__.lower(): m}).delete()
            return Response(status=status.HTTP_200_OK)
        return BadRequest(passwordSerializer.errors)


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


class QuantityMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = QuantitySerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return Quantity.objects.filter(store=self.request.user.staff.store)


class QuantitySingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = QuantitySerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        return Quantity.objects.filter(store=self.request.user.staff.store)
