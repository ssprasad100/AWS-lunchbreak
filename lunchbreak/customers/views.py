from django.http import Http404
from django.shortcuts import get_object_or_404
from lunch.models import Food, Menu, Store
from lunch.pagination import SimplePagination
from lunch.serializers import (FoodDetailSerializer, FoodSerializer,
                               MenuDetailSerializer, MenuSerializer,
                               StoreSerializer)
from lunch.views import StoreCategoryListViewBase
from Lunchbreak.views import TargettedViewSet
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from .authentication import CustomerAuthentication
from .config import DEMO_PHONE
from .models import Group, Heart, Order, PaymentLink, User, UserToken
from .serializers import (GroupSerializer, OrderDetailSerializer,
                          OrderedFoodPriceSerializer, OrderSerializer,
                          PaymentLinkSerializer, StoreHeartSerializer,
                          UserLoginSerializer, UserRegisterSerializer,
                          UserTokenSerializer, UserTokenUpdateSerializer)


class FoodViewSet(TargettedViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin):

    queryset = Food.objects.all()

    serializer_class_retrieve = FoodDetailSerializer
    serializer_class_list = FoodSerializer

    @property
    def queryset_retrieve(self):
        result = Food.objects.filter(
            deleted__isnull=True
        ).select_related(
            'foodtype',
            'menu',
        ).prefetch_related(
            'ingredientrelations__ingredient',
            'ingredientgroups',
        )

        return result

    @property
    def queryset_list(self):
        if 'menu_id' not in self.kwargs:
            raise Http404()

        return Food.objects.filter(
            menu_id=self.kwargs['menu_id'],
            deleted__isnull=True
        ).select_related(
            'menu',
            'foodtype',
        ).prefetch_related(
            'ingredients',  # Food.has_ingredients
        ).order_by(
            '-menu__priority',
            'menu__name',
            '-priority',
            'name'
        )


class MenuRetrieveView(generics.RetrieveAPIView):

    """List all menus."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = MenuDetailSerializer
    queryset = Menu.objects.select_related(
        'store',
    ).all()


class OrderViewSet(TargettedViewSet,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):

    authentication_classes = (CustomerAuthentication,)

    serializer_class_retrieve = OrderDetailSerializer
    serializer_class_create = OrderSerializer
    serializer_class_list = OrderSerializer

    queryset = Order.objects.all()
    queryset_retrieve = Order.objects.select_related(
        'store',
        'transaction',
        'user',
        'delivery_address',
        'group_order',
    ).prefetch_related(
        'orderedfood',
        'store__categories',
    ).all()

    @property
    def queryset_create(self):
        return self.queryset_list

    @property
    def queryset_list(self):
        return Order.objects.select_related(
            'store',
            'transaction',
            'user',
            'delivery_address',
            'group_order',
        ).filter(
            user=self.request.user
        ).order_by(
            '-receipt'
        )

    @list_route(methods=['post'], authentication_classes=())
    def price(self, request):
        """Return the price of the food."""
        serializer = OrderedFoodPriceSerializer(
            data=request.data,
            many=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class StoreViewSet(TargettedViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):

    authentication_classes = (CustomerAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'city', 'street',)

    serializer_class_retrieve = StoreHeartSerializer
    serializer_class_create = StoreSerializer
    serializer_class_list = StoreSerializer
    serializer_class_recent = StoreSerializer
    serializer_class_heart = StoreHeartSerializer
    serializer_class_unheart = StoreHeartSerializer
    serializer_class_paymentlink = PaymentLinkSerializer

    queryset = Store.objects.all()

    @property
    def object_retrieve(self):
        store = super(TargettedViewSet, self).get_object()
        store.hearted = self.request.user in store.hearts.all()
        return store

    @property
    def queryset_list(self):
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
            return Store.objects.nearby(
                self.kwargs['latitude'],
                self.kwargs['longitude'],
                proximity
            ).filter(
                enabled=True
            )
        else:
            return Store.objects.prefetch_related(
                'categories',
            ).filter(
                enabled=True
            ).distinct()

    @property
    def queryset_recent(self):
        result = Store.objects.prefetch_related(
            'categories',
        ).filter(
            placed_order__user=self.request.user,
            enabled=True
        ).order_by(
            '-placed_order__placed'
        ).distinct()
        return result

    @property
    def queryset_menu(self):
        # Check if filter for store_id is required
        return Menu.objects.filter(
            store_id=self.kwargs['pk']
        ).order_by(
            '-priority',
            'name'
        )

    @property
    def serializer_context_paymentlink(self):
        context = super(TargettedViewSet, self).get_serializer_context()
        context.update(
            {
                'store': self.get_object()
            }
        )
        return context

    def _heart(self, request, pk, option):
        store = self.get_object()

        if option == 'heart':
            heart, created = Heart.objects.get_or_create(
                store=store,
                user=request.user
            )
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(
                status=status_code
            )
        else:
            heart = get_object_or_404(
                Heart,
                store=store,
                user=request.user
            )
            heart.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @detail_route(methods=['patch'])
    def heart(self, request, pk=None):
        return self._heart(
            request=request,
            pk=pk,
            option='heart'
        )

    @detail_route(methods=['patch'])
    def unheart(self, request, pk=None):
        return self._heart(
            request=request,
            pk=pk,
            option='unheart'
        )

    @list_route(methods=['get'])
    def recent(self, request):
        self.kwargs['recent'] = True
        return self.list(request)

    @detail_route(methods=['post', 'get'])
    def paymentlink(self, request, pk=None):
        try:
            paymentlink = PaymentLink.objects.select_related(
                'redirectflow',
                'user',
                'store'
            ).get(
                user=request.user,
                store=self.get_object()
            )
            paymentlink = paymentlink if paymentlink.redirectflow.is_completed else None
        except PaymentLink.DoesNotExist:
            paymentlink = None

        if request.method == 'GET':
            if paymentlink is None:
                return Response(
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(
                paymentlink
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        else:
            serializer = self.get_serializer(
                paymentlink,
                data=request.data
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                    if paymentlink is None else status.HTTP_200_OK
                )


class StoreFoodViewSet(TargettedViewSet,
                       NestedViewSetMixin,
                       mixins.ListModelMixin):

    serializer_class = FoodSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @property
    def pagination_class(self):
        if 'menu_id' in self.kwargs:
            return None
        return SimplePagination

    @property
    def queryset(self):
        return Food.objects.filter(
            menu__store_id=self.kwargs['parent_lookup_pk'],
            deleted__isnull=True
        ).select_related(
            'menu__store',
            'foodtype',
        ).prefetch_related(
            'ingredients',  # Food.has_ingredients
        ).order_by(
            '-menu__priority',
            'menu__name',
            '-priority',
            'name'
        )


class StoreMenuViewSet(TargettedViewSet,
                       NestedViewSetMixin,
                       mixins.ListModelMixin):

    serializer_class = MenuSerializer
    pagination_class = SimplePagination

    @property
    def queryset(self):
        # Check if filter for store_id is required
        return Menu.objects.filter(
            store_id=self.kwargs['parent_lookup_pk']
        ).order_by(
            '-priority',
            'name'
        )


class StoreGroupViewSet(viewsets.GenericViewSet,
                        NestedViewSetMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):

    serializer_class = GroupSerializer
    authentication_classes = (CustomerAuthentication,)

    def get_queryset(self):
        return Group.objects.filter(
            store_id=self.kwargs['parent_lookup_pk'],
            members__in=[self.request.user]
        )


class StoreCategoryListView(StoreCategoryListViewBase):
    authentication_classes = (CustomerAuthentication,)


class UserViewSet(viewsets.GenericViewSet):

    queryset = User.objects.all()

    @list_route(methods=['post'])
    def register(self, request):
        serializer = UserRegisterSerializer(
            data=request.data
        )
        phone = request.data.get('phone', False)
        try:
            serializer.is_valid(raise_exception=True)
            return User.register(phone)
        except:
            if phone == DEMO_PHONE:
                return Response(status=status.HTTP_200_OK)
            raise

    @list_route(methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(
            data=request.data
        )
        phone = request.data.get('phone', False)

        try:
            serializer.is_valid(raise_exception=True)
            pin = request.data['pin']
            name = request.data.get('name', None)
            token = request.data.get('token', None)
            user = User.login(phone, pin, name, token)
            return UserToken.response(
                user=user,
                device=token['device'],
                service=token.get('service', SERVICE_INACTIVE),
                registration_id=token.get('registration_id', '')
            )
        except:
            if(phone == DEMO_PHONE and
                    'token' in request.data and
                    'device' in request.data['token'] and
                    'pin' in request.data):
                try:
                    user_demo = User.objects.get(
                        phone__phone=phone,
                        phone__pin=request.data['pin']
                    )
                    return UserToken.response(
                        user_demo,
                        request.data['token']['device']
                    )
                except User.DoesNotExist as e:
                    pass
            raise

    @list_route(methods=['get', 'put', 'patch'], authentication_classes=[CustomerAuthentication])
    def token(self, request):
        if request.method == 'GET':
            serializer = UserTokenSerializer(
                UserToken.objects.select_related(
                    'user',
                ).filter(
                    user=self.request.user
                ),
                many=True
            )
            return Response(
                serializer.data
            )
        else:
            serializer = UserTokenUpdateSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)

            request.auth.registration_id = request.data.get(
                'registration_id',
                request.auth.registration_id
            )
            request.auth.service = request.data.get(
                'service',
                request.auth.service
            )
            request.auth.save()
            return Response(
                status=status.HTTP_200_OK
            )
