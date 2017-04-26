import pendulum
from customers.config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_PLACED,
                              ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                              ORDER_STATUS_WAITING)
from customers.models import (ConfirmedOrder, Group, GroupOrder, Order,
                              OrderedFood)
from customers.serializers import (GroupOrderDetailSerializer,
                                   GroupOrderSerializer)
from django.conf import settings
from django.core.validators import validate_email
from django.db.models import Count
from django.http import Http404
from django.utils import timezone
from django_gocardless.serializers import \
    MerchantSerializer as GoCardlessMerchantSerializer
from lunch import views as lunch_views
from lunch.models import (Food, FoodType, HolidayPeriod, Ingredient,
                          IngredientGroup, Menu, Quantity, Store)
from lunch.serializers import (FoodTypeSerializer, MenuSerializer,
                               QuantityDetailSerializer)
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.views import TargettedViewSet
from payconiq.models import Merchant
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from .authentication import EmployeeAuthentication, StaffAuthentication
from .exceptions import InvalidDatetime, InvalidEmail, InvalidPasswordReset
from .mixins import SafeDeleteModelMixin
from .models import Employee, Staff
from .permissions import StoreOwnerOnlyPermission, StoreOwnerPermission
from .serializers import (EmployeeSerializer, FoodDetailSerializer,
                          FoodSerializer, GroupSerializer,
                          IngredientGroupDetailSerializer,
                          IngredientGroupSerializer, IngredientSerializer,
                          OrderDetailSerializer, OrderedFoodSerializer,
                          OrderSerializer, OrderSpreadSerializer,
                          PopularFoodSerializer, StaffSerializer,
                          StoreDetailSerializer, StoreGoCardlessSerializer,
                          StoreHeaderSerializer, StorePayconiqSerializer)

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
            # TODO Make this depend on the Store's timezone
            return pendulum.parse(
                datetime_string
            ).timezone_(
                settings.TIME_ZONE
            )._datetime
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
        serializer.is_valid(raise_exception=True)

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
        except LunchbreakException:
            return InvalidEmail().response
        except model.DoesNotExist:
            return InvalidPasswordReset().response

        m.password_reset = ''
        m.set_password(request.data['password'])
        m.save()

        token_model.objects.filter(
            **{
                model.__name__.lower(): m
            }
        ).delete()
        return Response(status=status.HTTP_200_OK)


class ResetRequestView(generics.CreateAPIView):

    def post(self, request, authentication, *args, **kwargs):
        return authentication.password_reset_request(request)


class StoreViewSet(TargettedViewSet,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    permission_classes = (StoreOwnerPermission,)

    serializer_class = StoreDetailSerializer
    serializer_class_header = StoreHeaderSerializer
    serializer_class_merchant = GoCardlessMerchantSerializer

    queryset = Store.objects.all()

    @property
    def parser_classes(self):
        parser_classes = super().parser_classes
        parser_classes.append(FileUploadParser)
        return parser_classes

    @detail_route(methods=['get', 'post'])
    def header(self, request, pk=None):
        if request.method == 'GET':
            return lunch_views.StoreHeaderView.as_view()(
                request=request,
                store_id=pk
            )
        else:
            self.kwargs['filename'] = 'attachment; filename=storeheader{store_id}.jpg'.format(
                store_id=pk
            )
            request.data['original'] = request.data.pop('file')
            serializer = self.get_serializer_class()(
                data=request.data,
                context={
                    'request': request
                }
            )
            if serializer.is_valid(raise_exception=True):
                store = request.user.staff.store
                if hasattr(store, 'header'):
                    store.header.delete()
                serializer.save()
                return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=[StoreOwnerOnlyPermission])
    def merchant(self, request, pk=None):
        """Create a GoCardless Merchant.

        .. deprecated:: 2.2.0
            Use /store/{pk}/gocardless instead.
        """

        store = self.get_object()

        if store.staff.is_merchant:
            return Response(
                self.get_serializer_class()(
                    store.staff.gocardless
                ).data
            )

        if store.staff.gocardless is not None:
            store.staff.gocardless.delete()

        merchant, url = Merchant.authorisation_link(
            email=store.staff.email
        )
        store.staff.gocardless = merchant
        store.staff.save()

        return Response(
            StoreGoCardlessSerializer(url).data
        )


class StorePayconiqViewSet(TargettedViewSet,
                           NestedViewSetMixin,
                           mixins.RetrieveModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin):
    # TODO Implement the same for GoCardless
    authentication_classes = (StoreOwnerOnlyPermission,)
    serializer_class = StorePayconiqSerializer

    def get_queryset(self):
        return Merchant.objects.filter(
            store_id=self.kwargs['parent_lookup_pk']
        )


class FoodViewSet(TargettedViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  SafeDeleteModelMixin):

    serializer_class = FoodSerializer
    serializer_class_retrieve = FoodDetailSerializer
    serializer_class_popular = PopularFoodSerializer

    authentication_classes = (EmployeeAuthentication,)
    permission_classes = [StoreOwnerPermission]

    @property
    def queryset(self):
        return Food.objects.filter(
            menu__store=self.request.user.staff.store
        )

    @property
    def queryset_list(self):
        since = datetime_request(self.request, arg='since')
        if since is not None:
            result = Food.objects.filter(
                menu__store=self.request.user.staff.store,
                last_modified__gte=since
            )
        else:
            result = Food.objects.filter(
                menu__store=self.request.user.staff.store
            )

        return result.order_by('-priority', 'name')

    @property
    def queryset_popular(self):
        frm = datetime_request(self.request, arg='from')

        if frm is not None:
            to = datetime_request(self.request, arg='to')
            to = to if to is not None else timezone.now()
            return Food.objects.filter(
                menu__store_id=self.request.user.staff.store_id,
                orderedfood__placed_order__receipt__gt=frm,
                orderedfood__placed_order__receipt__lt=to
            ).annotate(
                orderedfood_count=Count('orderedfood')
            ).order_by('-orderedfood_count')
        else:
            raise Http404()

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
        # TODO Check whether this still is needed
        serializer.save(store=self.store)


class MenuViewSet(TargettedViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  SafeDeleteModelMixin):

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


class IngredientViewSet(TargettedViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        SafeDeleteModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = IngredientSerializer
    permission_classes = (StoreOwnerPermission,)

    def get_queryset(self):
        since = datetime_request(self.request, arg='datetime')
        if since is not None:
            return Ingredient.objects.filter(
                group__store=self.request.user.staff.store,
                last_modified__gte=since
            )
        return Ingredient.objects.filter(
            group__store=self.request.user.staff.store
        )

    @property
    def queryset_list(self):
        return self.get_queryset().order_by(
            '-priority',
            'name'
        )


# class IngredientView(PerformCreateStore, generics.ListAPIView):
#     authentication_classes = (EmployeeAuthentication,)
#     serializer_class = IngredientSerializer
#     permission_classes = (StoreOwnerPermission,)

#     def get_queryset(self):
#         result = Ingredient.objects.filter(
#             group__store=self.request.user.staff.store
#         )
#         since = datetime_request(self.request, arg='since')
#         if since is not None:
#             return result.filter(last_modified__gte=since)
#         return result


# class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
#     authentication_classes = (EmployeeAuthentication,)
#     serializer_class = IngredientSerializer
#     permission_classes = (StoreOwnerPermission,)

#     def get_queryset(self):
#         since = datetime_request(self.request, arg='datetime')
#         if since is not None:
#             result = Ingredient.objects.filter(
#                 group__store=self.request.user.staff.store,
#                 last_modified__gte=since
#             )
#         else:
#             result = Ingredient.objects.filter(
#                 group__store=self.request.user.staff.store
#             )
#         return result.order_by('-priority', 'name')


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
                return ConfirmedOrder.objects.filter(**filters).order_by('receipt')
            else:
                if since is not None:
                    filters['placed__gt'] = since
                return ConfirmedOrder.objects.filter(**filters).order_by('-placed')
        return ConfirmedOrder.objects.filter(**filters)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderDetailSerializer
    pagination_class = None

    def get_queryset(self):
        return ConfirmedOrder.objects.filter(
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


class OrderedFoodViewSet(TargettedViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = OrderedFoodSerializer

    def get_queryset(self):
        return OrderedFood.objects.filter(
            original__menu__store_id=self.request.user.staff.store_id
        )


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


class StoreCategoryView(lunch_views.StoreCategoryListViewBase):
    authentication_classes = (EmployeeAuthentication,)


class StoreGroupViewSet(TargettedViewSet,
                        NestedViewSetMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.filter(
            store_id=self.kwargs['parent_lookup_pk']
        )


class StoreGroupOrderViewSet(TargettedViewSet,
                             NestedViewSetMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    serializer_class = GroupOrderSerializer
    serializer_class_retrieve = GroupOrderDetailSerializer

    def get_queryset(self):
        return GroupOrder.objects.filter(
            group__store_id=self.kwargs['parent_lookup_pk']
        )


class StoreOpeningPeriodViewSet(lunch_views.StoreOpeningPeriodViewSet,
                                mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    permission_classes = (StoreOwnerPermission,)


class StoreHolidayPeriodViewSet(lunch_views.StoreHolidayPeriodViewSet,
                                mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin):
    authentication_classes = (EmployeeAuthentication,)
    permission_classes = (StoreOwnerPermission,)

    @classmethod
    def _get_queryset(cls, parent_pk):
        return HolidayPeriod.objects.filter(
            store_id=parent_pk
        )
