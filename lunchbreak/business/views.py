from customers.config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_PLACED,
                              ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                              ORDER_STATUS_WAITING)
from customers.models import Order, Reservation
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lunch.models import (Food, FoodCategory, FoodType, Ingredient,
                          IngredientGroup, Quantity, Store)
from lunch.responses import BadRequest
from lunch.serializers import (FoodTypeSerializer, QuantitySerializer,
                               ShortFoodCategorySerializer)
from lunch.views import (HolidayPeriodListViewBase, OpeningPeriodListViewBase,
                         OpeningListViewBase, StoreCategoryListViewBase)
from Lunchbreak.views import TargettedViewSet
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from .authentication import EmployeeAuthentication, StaffAuthentication
from .exceptions import InvalidDatetime, InvalidEmail, InvalidPasswordReset
from .models import Employee, Staff
from .permissions import StoreOwnerPermission
from .serializers import (EmployeeSerializer, IngredientGroupSerializer,
                          IngredientSerializer, OrderSerializer,
                          OrderSpreadSerializer, ReservationSerializer,
                          ShortFoodSerializer, ShortIngredientGroupSerializer,
                          ShortOrderSerializer, SingleFoodSerializer,
                          StaffSerializer, StoreSerializer, StoreSerializerV3)

AVAILABLE_STATUSES = [
    ORDER_STATUS_PLACED,
    ORDER_STATUS_RECEIVED,
    ORDER_STATUS_STARTED,
    ORDER_STATUS_WAITING
]


def datetime_request(request, kwargs, arg, method_check=False):
    if (method_check or request.method == 'GET') and \
        arg in kwargs and \
            kwargs[arg] is not None:
        datetime_string = kwargs[arg]
        try:
            return timezone.datetime.strptime(
                datetime_string,
                settings.DATETIME_FORMAT_URL
            )
        except ValueError:
            try:
                return timezone.datetime.strptime(
                    datetime_string,
                    '%d-%m-%Y-%H-%M-%S'
                )
            except ValueError:
                raise InvalidDatetime()
    return None


class EmployeeView(generics.ListAPIView):
    authentication_classes = (StaffAuthentication,)
    serializer_class = EmployeeSerializer
    pagination_class = None

    def get_queryset(self):
        return Employee.objects.filter(staff=self.request.user)

    def post(self, request, *args, **kwargs):
        return EmployeeAuthentication.login(request)


class PasswordResetView(generics.CreateAPIView):

    def post(self, request, model, token_model, serializer_class,
             employee=False, *args, **kwargs):
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            email = request.data['email']
            password_reset = request.data['password_reset']

            try:
                validate_email(email)
                if employee:
                    m = model.objects.get(
                        staff__email=email,
                        password_reset=password_reset
                    )
                else:
                    m = model.objects.get(
                        email=email,
                        password_reset=password_reset
                    )
            except ValidationError:
                return InvalidEmail().response
            except model.DoesNotExist:
                return InvalidPasswordReset().response

            m.password_reset = None
            m.set_password(request.data['password'])
            m.save()

            token_model.objects.filter(
                **{
                    model.__name__.lower(): m
                }
            ).delete()
            return Response(status=status.HTTP_200_OK)
        return BadRequest(serializer.errors)


class ResetRequestView(generics.CreateAPIView):

    def post(self, request, authentication, *args, **kwargs):
        return authentication.password_reset_request(request)


class FoodViewSet(TargettedViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin):

    serializer_class = ShortFoodSerializer
    serializer_class_retrieve = SingleFoodSerializer

    authentication_classes = (EmployeeAuthentication,)

    @property
    def queryset(self):
        return Food.objects.filter(
            store=self.request.user.staff.store
        )

    @property
    def queryset_list(self):
        since = datetime_request(self.request, self.kwargs, arg='since')
        if since is not None:
            result = Food.objects.filter(
                store=self.request.user.staff.store,
                last_modified__gte=since
            )
        else:
            result = Food.objects.filter(
                store=self.request.user.staff.store
            )

        return result.order_by('-priority', 'name')

    @property
    def queryset_popular(self):
        frm = datetime_request(self.request, self.kwargs, arg='frm')

        if frm is not None:
            to = datetime_request(self.request, self.kwargs, arg='to')
            to = to if to is not None else timezone.now()
            return Food.objects.filter(
                store_id=self.request.user.staff.store_id,
                orderedfood__order__receipt__gt=frm,
                orderedfood__order__receipt__lt=to
            ).annotate(
                orderedfood_count=Count('orderedfood')
            ).order_by('-orderedfood_count')
        else:
            raise Http404()

    @list_route(methods=['post'], permission_classes=[StoreOwnerPermission])
    def list(self, request):
        return super(FoodViewSet, self).list(request)

    @detail_route(methods=['patch'], permission_classes=[StoreOwnerPermission])
    def update(self, request, pk=None):
        return super(FoodViewSet, self).update(request, pk)

    @detail_route(methods=['delete'], permission_classes=[StoreOwnerPermission])
    def delete(self, request, pk=None):
        food = self.get_object()
        food.delete()

        if food.pk is not None:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def popular(self, request):
        return self._list(request)


class ListCreateStoreView(generics.ListCreateAPIView):

    def perform_create(self, serializer):
        store = self.request.user.staff.store \
            if isinstance(self.request.user, Employee) \
            else self.request.user.store
        serializer.save(store=store)


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
        return FoodCategory.objects.filter(
            store=self.request.user.staff.store
        )


class FoodTypeListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = FoodTypeSerializer
    pagination_class = None
    queryset = FoodType.objects.all()


class IngredientMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        result = Ingredient.objects.filter(store=self.request.user.staff.store)
        since = datetime_request(self.request, self.kwargs, arg='datetime')
        if since is not None:
            return result.filter(last_modified__gte=since)
        return result


class IngredientSingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        since = datetime_request(self.request, self.kwargs, arg='datetime')
        if since is not None:
            result = Ingredient.objects.filter(
                store=self.request.user.staff.store,
                last_modified__gte=since
            )
        else:
            result = Ingredient.objects.filter(
                store=self.request.user.staff.store
            )
        return result.order_by('-priority', 'name')


class IngredientGroupMultiView(ListCreateStoreView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortIngredientGroupSerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return IngredientGroup.objects.filter(
            store=self.request.user.staff.store
        )


class IngredientGroupSingleView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientGroupSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        return IngredientGroup.objects.filter(
            store=self.request.user.staff.store
        )


class OrderListView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ShortOrderSerializer

    def get_queryset(self):
        filters = {
            'store': self.request.user.staff.store,
            'status__in': AVAILABLE_STATUSES
        }

        if self.request.method == 'GET':
            since = datetime_request(
                self.request,
                self.kwargs,
                arg='datetime',
                method_check=True
            )

            if 'option' in self.kwargs \
                    and self.kwargs['option'] == 'receipt':
                if since is not None:
                    filters['receipt__gt'] = since
                return Order.objects.filter(**filters).order_by('receipt')
            else:
                if since is not None:
                    filters['placed__gt'] = since
                return Order.objects.filter(**filters).order_by('-placed')
        return Order.objects.filter(**filters)


class OrderUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(
            store=self.request.user.staff.store,
            status__in=AVAILABLE_STATUSES
        )


class OrderSpreadView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSpreadSerializer

    def list(self, request, unit, frm, to=None):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)

    def get_queryset(self):
        unit = self.kwargs['unit']

        store_id = self.request.user.staff.store_id

        frm = datetime_request(self.request, self.kwargs, arg='frm')
        to = datetime_request(self.request, self.kwargs, arg='to')
        if to is None:
            to = timezone.now()

        return Order.objects.raw('''
            SELECT
                customers_order.*,
                COUNT(customers_order.id) as amount,
                SUM(customers_order.total) as sm,
                AVG(customers_order.total) as average,
                {unit}(customers_order.receipt) as unit
            FROM
                customers_order
            WHERE
                customers_order.receipt > %s
                AND customers_order.receipt < %s
                AND customers_order.store_id = %s
                AND customers_order.status = %s
            GROUP BY
                unit
            ORDER BY
                unit;
        '''.format(
            unit=unit
        ), [frm, to, store_id, ORDER_STATUS_COMPLETED])


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


class ReservationMultiView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(store_id=self.request.user.staff.store_id)


class ReservationSingleView(generics.UpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(store_id=self.request.user.staff.store_id)


class StaffMultiView(generics.ListAPIView):
    serializer_class = StaffSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] \
            if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            stores = Store.objects.nearby(
                self.kwargs['latitude'],
                self.kwargs['longitude'],
                proximity
            )
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


class StoreSingleView(generics.RetrieveUpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    permission_classes = (StoreOwnerPermission,)

    def get_serializer_class(self):
        if self.request.version >= 4:
            return StoreSerializer
        else:
            return StoreSerializerV3

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def get_queryset(self):
        return Store.objects.filter(
            id=self.request.user.staff.store_id
        )


class GetStoreMixin(object):

    def get_store_id(self):
        return self.request.user.staff.store_id


class OpeningPeriodListView(GetStoreMixin, OpeningPeriodListViewBase):
    authentication_classes = (EmployeeAuthentication,)


class HolidayPeriodListView(GetStoreMixin, HolidayPeriodListViewBase):
    authentication_classes = (EmployeeAuthentication,)


class StoreOpenView(GetStoreMixin, OpeningListViewBase):
    authentication_classes = (EmployeeAuthentication,)


class StoreCategoryListView(GetStoreMixin, StoreCategoryListViewBase):
    authentication_classes = (EmployeeAuthentication,)
