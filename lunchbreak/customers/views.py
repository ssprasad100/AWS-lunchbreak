from django.http import Http404
from django.shortcuts import get_object_or_404
from lunch.models import Food, IngredientGroup, Menu, Store
from lunch.pagination import SimplePagination
from lunch.renderers import JPEGRenderer
from lunch.responses import BadRequest, DoesNotExist
from lunch.serializers import (FoodDetailSerializer, FoodSerializer,
                               MenuDetailSerializer, MenuSerializer,
                               StoreSerializer)
from lunch.views import (HolidayPeriodListViewBase, OpeningListViewBase,
                         OpeningPeriodListViewBase, StoreCategoryListViewBase)
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.views import TargettedViewSet
from push_notifications.models import SERVICE_INACTIVE
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.mixins import NestedViewSetMixin

from .authentication import CustomerAuthentication
from .config import DEMO_DIGITS_ID, DEMO_PHONE
from .models import (Heart, Order, OrderedFood, PaymentLink, Reservation, User,
                     UserToken)
from .serializers import (GroupSerializer, InviteSerializer,
                          InviteUpdateSerializer, OrderDetailSerializer,
                          OrderedFoodPriceSerializer, OrderSerializer,
                          PaymentLinkSerializer, ReservationSerializer,
                          StoreHeartSerializer, UserLoginSerializer,
                          UserRegisterSerializer, UserTokenSerializer,
                          UserTokenUpdateSerializer)


class FoodViewSet(TargettedViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin):

    queryset = Food.objects.all()

    serializer_class_retrieve = FoodDetailSerializer
    serializer_class_list = FoodSerializer

    @property
    def queryset_retrieve(self):
        result = Food.objects.filter(
            deleted=False
        ).select_related(
            'foodtype',
            'menu',
        ).prefetch_related(
            'ingredientrelation_set__ingredient',
            'ingredientgroups',
        )

        return result

    @property
    def queryset_list(self):
        if 'menu_id' not in self.kwargs:
            raise Http404()

        return Food.objects.filter(
            menu_id=self.kwargs['menu_id'],
            deleted=False
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

    """List all food categories."""

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
    ).all()

    @property
    def queryset_create(self):
        return self.queryset_list

    @property
    def queryset_list(self):
        return Order.objects.select_related(
            'store',
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
            many=True
        )
        if serializer.is_valid(raise_exception=True):
            result = []
            for price_check in serializer.validated_data:
                price_info = {}
                original = price_check['original']
                if 'ingredients' in price_check:
                    ingredients = price_check['ingredients']
                    food_closest = Food.objects.closest(ingredients, original)
                    IngredientGroup.check_ingredients(ingredients, food_closest)

                    price_info['cost'] = OrderedFood.calculate_cost(ingredients, food_closest)
                    price_info['food'] = food_closest.id
                else:
                    price_info['cost'] = original.cost
                    price_info['food'] = original.id

                # TODO make it into 1 filter/query
                price_info['food'] = FoodSerializer().to_representation(
                    instance=Food.objects.get(
                        id=price_info['food']
                    )
                )
                result.append(price_info)
            return Response(data=result, status=status.HTTP_200_OK)


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
            order__user=self.request.user,
            enabled=True
        ).order_by(
            '-order__placed'
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

    @detail_route(methods=['post', 'get'])
    def paymentlink(self, request, pk=None):
        try:
            paymentlink = PaymentLink.objects.get(
                user=request.user,
                store=self.get_object()
            )
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

    @list_route(methods=['get'])
    def recent(self, request):
        self.kwargs['recent'] = True
        return self.list(request)


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
            store_id=self.kwargs['parent_lookup_pk'],
            deleted=False
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


class ReservationSingleView(generics.RetrieveUpdateAPIView):

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        )


class GetStoreMixin(object):

    def get_store_id(self):
        return self.kwargs['pk']


class OpeningPeriodListView(GetStoreMixin, OpeningPeriodListViewBase):
    authentication_classes = (CustomerAuthentication,)


class HolidayPeriodListView(GetStoreMixin, HolidayPeriodListViewBase):
    authentication_classes = (CustomerAuthentication,)


class StorePeriodsView(GetStoreMixin, OpeningListViewBase):
    authentication_classes = (CustomerAuthentication,)


class StoreHeaderView(APIView):

    renderer_classes = (JPEGRenderer,)

    def get(self, request, store_id, width, height):
        store = get_object_or_404(Store, id=store_id)
        if store.header is None:
            raise Http404('That store does not have a header.')
        image = store.header.retrieve_from_source(
            'original',
            int(width),
            int(height)
        )
        image.open()
        return Response(image)


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
        if serializer.is_valid():
            return User.register(phone)
        elif phone == DEMO_PHONE:
            return Response(status=status.HTTP_200_OK)
        return BadRequest(serializer.errors)

    @list_route(methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(
            data=request.data
        )
        phone = request.data.get('phone', False)
        if serializer.is_valid():
            pin = request.data['pin']
            name = request.data.get('name', None)
            token = request.data.get('token', None)
            try:
                user = User.login(phone, pin, name, token)
            except LunchbreakException as e:
                return e.response
            if user is not None:
                return UserToken.response(
                    user=user,
                    device=token['device'],
                    service=token.get('service', SERVICE_INACTIVE),
                    registration_id=token.get('registration_id', '')
                )
            return DoesNotExist()
        elif(phone == DEMO_PHONE and
                'token' in request.data and
                'device' in request.data['token'] and
                'pin' in request.data):
            try:
                user_demo = User.objects.get(
                    phone=phone,
                    request_id=request.data['pin'],
                    digits_id=DEMO_DIGITS_ID
                )
                return UserToken.response(
                    user_demo,
                    request.data['token']['device']
                )
            except User.DoesNotExist:
                pass
        return BadRequest(serializer.errors)

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
            if serializer.is_valid(raise_exception=True):
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
        return BadRequest(serializer.errors)


class GroupView(generics.ListCreateAPIView):

    authentication_classes = (CustomerAuthentication,)
    serializer_class = GroupSerializer
    authenticated_user = 'leader'

    def get_queryset(self):
        return self.request.user.group_set.all()


class InviteView(object):

    authentication_classes = (CustomerAuthentication,)
    serializer_class = InviteSerializer

    def get_queryset(self):
        return self.request.user.invite_set.all()


class InviteMultiView(InviteView, generics.ListCreateAPIView):
    pass


class InviteSingleView(InviteView, generics.UpdateAPIView):
    serializer_class = InviteUpdateSerializer


class ReservationMultiView(generics.ListCreateAPIView):

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        )
