import arrow
from customers.config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_PLACED,
                              ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                              ORDER_STATUS_WAITING)
from customers.models import Order, Reservation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect
from django.utils import timezone
from django_gocardless.models import Merchant
from django_gocardless.serializers import MerchantSerializer
from lunch.models import (Food, FoodType, Ingredient, IngredientGroup, Menu,
                          Quantity, Store)
from lunch.responses import BadRequest
from lunch.serializers import (FoodTypeSerializer, MenuSerializer,
                               QuantityDetailSerializer)
from lunch.views import StoreCategoryListViewBase
from Lunchbreak.views import TargettedViewSet
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from .authentication import EmployeeAuthentication, StaffAuthentication
from .exceptions import InvalidDatetime, InvalidEmail, InvalidPasswordReset
from .models import Employee, Staff
from .permissions import StoreOwnerOnlyPermission, StoreOwnerPermission
from .serializers import (EmployeeSerializer, FoodDetailSerializer,
                          FoodSerializer, IngredientGroupDetailSerializer,
                          IngredientGroupSerializer, IngredientSerializer,
                          OrderDetailSerializer, OrderSerializer,
                          OrderSpreadSerializer, ReservationSerializer,
                          StaffSerializer, StoreDetailSerializer)

AVAILABLE_STATUSES = [
    ORDER_STATUS_PLACED,
    ORDER_STATUS_RECEIVED,
    ORDER_STATUS_STARTED,
    ORDER_STATUS_WAITING
]


def datetime_request(request, arg, method_check=False):
    if (method_check or request.method == 'GET') and \
            arg in request.GET and request.GET[arg] is not None:
        datetime_string = request.GET[arg]
        try:
            return arrow.get(
                datetime_string
            ).datetime
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

    def post(self, request, model, token_model, serializer_class, employee=False):
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


class StoreViewSet(TargettedViewSet,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    permission_classes = (StoreOwnerPermission,)
    serializer_class = StoreDetailSerializer
    serializer_class_merchant = MerchantSerializer
    queryset = Store.objects.all()

    @detail_route(methods=['get'], permission_classes=[StoreOwnerOnlyPermission])
    def merchant(self, request, pk=None):
        store = self.get_object()

        if store.staff.is_merchant:
            return Response(
                self.get_serializer_class()(
                    store.staff.merchant
                ).data
            )

        if store.staff.merchant is not None:
            store.staff.merchant.delete()

        merchant, url = Merchant.authorisation_link(
            email=store.staff.email
        )
        store.staff.merchant = merchant
        store.staff.save()

        return redirect(
            to=url
        )


class FoodViewSet(TargettedViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):

    serializer_class = FoodSerializer
    serializer_class_retrieve = FoodDetailSerializer

    authentication_classes = (EmployeeAuthentication,)
    permission_classes = [StoreOwnerPermission]

    @property
    def pagination_class_list(self):
        return None

    @property
    def queryset(self):
        return Food.objects.filter(
            store=self.request.user.staff.store
        )

    @property
    def queryset_list(self):
        since = datetime_request(self.request, arg='since')
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
        frm = datetime_request(self.request, arg='from')

        if frm is not None:
            to = datetime_request(self.request, arg='to')
            to = to if to is not None else timezone.now()
            return Food.objects.filter(
                store_id=self.request.user.staff.store_id,
                orderedfood__placed_order__receipt__gt=frm,
                orderedfood__placed_order__receipt__lt=to
            ).annotate(
                orderedfood_count=Count('orderedfood')
            ).order_by('-orderedfood_count')
        else:
            raise Http404()

    @detail_route(methods=['delete'], permission_classes=[StoreOwnerPermission])
    def delete(self, request, pk=None):
        food = self.get_object()
        food.delete()

        if food.pk is not None:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def popular(self, request):
        result = self._list(request)
        return result


class StoreSenderView:

    @property
    def store(self):
        return self.request.user.staff.store \
            if isinstance(self.request.user, Employee) \
            else self.request.user.store


class PerformCreateStore(StoreSenderView, generics.CreateAPIView):

    def perform_create(self, serializer):
        serializer.save(store=self.store)


class MenuViewSet(TargettedViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):

    authentication_classes = (EmployeeAuthentication,)
    permission_classes = (StoreOwnerPermission,)

    serializer_class = MenuSerializer

    pagination_class_list = None

    def get_queryset(self):
        return Menu.objects.filter(
            store=self.request.user.staff.store
        )


class FoodTypeView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = FoodTypeSerializer
    pagination_class = None
    queryset = FoodType.objects.all()


class IngredientView(PerformCreateStore, generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        result = Ingredient.objects.filter(
            store=self.request.user.staff.store
        )
        since = datetime_request(self.request, arg='since')
        if since is not None:
            return result.filter(last_modified__gte=since)
        return result


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        since = datetime_request(self.request, arg='datetime')
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


class IngredientGroupView(PerformCreateStore, generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientGroupSerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return IngredientGroup.objects.filter(
            store=self.request.user.staff.store
        )


class IngredientGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientGroupDetailSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        return IngredientGroup.objects.filter(
            store=self.request.user.staff.store
        )


class OrderView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        filters = {
            'store': self.request.user.staff.store,
            'status__in': AVAILABLE_STATUSES
        }

        if self.request.method == 'GET':
            since = datetime_request(
                self.request,
                arg='since',
                method_check=True
            )

            if 'order_by' in self.request.GET \
                    and self.request.GET['order_by'] == 'receipt':
                if since is not None:
                    filters['receipt__gt'] = since
                return Order.objects.filter(**filters).order_by('receipt')
            else:
                if since is not None:
                    filters['placed__gt'] = since
                return Order.objects.filter(**filters).order_by('-placed')
        return Order.objects.filter(**filters)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderDetailSerializer
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(
            store_id=self.request.user.staff.store_id,
            status__in=AVAILABLE_STATUSES
        )


class OrderSpreadView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderSpreadSerializer
    units = [
        'hour',
        'week',
        'weekday',
        'day',
        'month',
        'quarter',
        'year'
    ]

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)

    def get_queryset(self):
        unit = self.request.query_params.get('unit')
        if unit not in self.units:
            raise Http404()

        store_id = self.request.user.staff.store_id

        frm = datetime_request(self.request, arg='from')

        if frm is None:
            raise Http404()

        to = datetime_request(self.request, arg='to')
        if to is None:
            to = timezone.now()

        return Order.objects.raw('''
            SELECT
                customers_order.id,
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
                customers_order.id,
                unit
            ORDER BY
                unit;
        '''.format(
            unit=unit
        ), [frm, to, store_id, ORDER_STATUS_COMPLETED])


class QuantityView(PerformCreateStore, generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = QuantityDetailSerializer
    permission_classes = (StoreOwnerPermission,)
    pagination_class = None

    def get_queryset(self):
        return Quantity.objects.filter(
            store_id=self.request.user.staff.store_id
        )


class QuantityDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = QuantityDetailSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        return Quantity.objects.filter(
            store_id=self.request.user.staff.store_id
        )


class ReservationView(generics.ListAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(
            store_id=self.request.user.staff.store_id
        )


class ReservationDetailView(generics.UpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(
            store_id=self.request.user.staff.store_id
        )


class StaffView(generics.ListAPIView):
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


class StaffDetailView(generics.RetrieveAPIView):
    authentication_classes = (StaffAuthentication,)
    serializer_class = StaffSerializer

    def get_queryset(self):
        return Staff.objects.filter(
            id=self.request.user.id
        )


class StoreCategoryView(StoreCategoryListViewBase):
    authentication_classes = (EmployeeAuthentication,)
