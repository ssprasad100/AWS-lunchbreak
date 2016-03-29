from django.http import Http404
from django.shortcuts import get_object_or_404
from lunch.models import Food, FoodCategory, IngredientGroup, Store
from lunch.pagination import SimplePagination
from lunch.renderers import JPEGRenderer
from lunch.responses import BadRequest
from lunch.serializers import (FoodCategorySerializer, MultiFoodSerializer,
                               ShortFoodCategorySerializer,
                               ShortStoreSerializer, SingleFoodSerializer)
from lunch.views import (HolidayPeriodListViewBase, OpeningHoursListViewBase,
                         OpeningListViewBase, StoreCategoryListViewBase)
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CustomerAuthentication
from .config import DEMO_DIGITS_ID, DEMO_PHONE
from .models import Heart, Order, OrderedFood, Reservation, User, UserToken
from .serializers import (GroupSerializer, InviteSerializer,
                          InviteUpdateSerializer, MultiUserTokenSerializer,
                          OrderedFoodPriceSerializer, OrderSerializer,
                          ReservationSerializer, ShortOrderSerializer,
                          StoreHeartSerializer, UserLoginSerializer,
                          UserRegisterSerializer, UserTokenUpdateSerializer)


class FoodRetrieveView(generics.RetrieveAPIView):

    """Retrieve a specific food."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = SingleFoodSerializer

    def get_queryset(self):
        return Food.objects.select_related(
            'foodtype',
            'category',
        ).filter(
            deleted=False
        ).prefetch_related(
            'ingredientrelation_set__ingredient',
            'ingredientgroups',
        )


class FoodCategoryRetrieveView(generics.RetrieveAPIView):

    """List all food categories."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.select_related(
        'store',
    ).all()


class TargettedViewSet(object):

    def get_attr_action(self, attribute):
        action_attribute = '{attribute}_{action}'.format(
            attribute=attribute,
            action=self.action
        )
        if hasattr(self, action_attribute):
            return getattr(self, action_attribute)
        return getattr(self, attribute)

    def get_serializer_class(self):
        return self.get_attr_action('serializer_class') or \
            super(TargettedViewSet, self).get_serializer_class()

    def get_queryset(self):
        return self.get_attr_action('queryset') or \
            super(TargettedViewSet, self).get_queryset()

    def get_pagination_class(self):
        return self.get_attr_action('pagination_class') or \
            super(TargettedViewSet, self).get_pagination_class()

    def _list(self, request):
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class CreateListRetrieveViewSet(TargettedViewSet,
                                mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):

    """ViewSet that provides `retrieve`, `create` and `list` actions.

    Allows for a `.retrieve_serializer_class`, `.create_serializer_class`,
    `.list_serializer_class` to be used.
    """
    pass


class OrderViewSet(CreateListRetrieveViewSet):

    authentication_classes = (CustomerAuthentication,)

    serializer_class_retrieve = OrderSerializer
    serializer_class_create = ShortOrderSerializer
    serializer_class_list = ShortOrderSerializer

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
            '-pickup'
        )

    @list_route(methods=['post'])
    def price(self, request):
        """Return the price of the food."""
        serializer = OrderedFoodPriceSerializer(
            data=request.data,
            many=True
        )
        if serializer.is_valid():
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
                result.append(price_info)
            return Response(data=result, status=status.HTTP_200_OK)
        return BadRequest(serializer.errors)


class StoreViewSet(TargettedViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):

    authentication_classes = (CustomerAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'city', 'street',)

    serializer_class_retrieve = ShortStoreSerializer
    serializer_class_create = ShortStoreSerializer
    serializer_class_list = ShortStoreSerializer
    serializer_class_food = MultiFoodSerializer
    serializer_class_foodcategory = ShortFoodCategorySerializer
    serializer_class_heart = StoreHeartSerializer
    serializer_class_unheart = StoreHeartSerializer

    queryset = Store.objects.all()

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
            result = Store.objects.prefetch_related(
                'categories',
            ).filter(
                enabled=True
            ).distinct()
            if 'recent' in self.kwargs:
                result = result.filter(
                    order__user=self.request.user
                ).order_by(
                    '-order__placed'
                )
            return result

    @property
    def pagination_class_food(self):
        if 'foodcategory_id' in self.kwargs:
            return None
        return SimplePagination

    @property
    def queryset_food(self):
        if 'pk' in self.kwargs:
            result = Food.objects.filter(
                store_id=self.kwargs['pk'],
                deleted=False
            )
        elif 'foodcategory_id' in self.kwargs:
            result = Food.objects.filter(
                category_id=self.kwargs['foodcategory_id'],
                deleted=False
            )
        return result.select_related(
            'category',
            'foodtype',
        ).prefetch_related(
            'ingredients',  # Food.has_ingredients
        ).order_by(
            '-category__priority',
            'category__name',
            '-priority',
            'name'
        )

    @property
    def queryset_foodcategory(self):
        # Check if filter for store_id is required
        return FoodCategory.objects.filter(
            store_id=self.kwargs['pk']
        ).order_by(
            '-priority',
            'name'
        )

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

    @detail_route(methods=['get'])
    def food(self, request, pk=None, foodcategory_id=None):
        return self._list(request)

    @detail_route(methods=['get'])
    def foodcategory(self, request, pk=None):
        return self._list(request)


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


class OpeningHoursListView(GetStoreMixin, OpeningHoursListViewBase):
    authentication_classes = (CustomerAuthentication,)


class HolidayPeriodListView(GetStoreMixin, HolidayPeriodListViewBase):
    authentication_classes = (CustomerAuthentication,)


class StoreHoursView(GetStoreMixin, OpeningListViewBase):
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
            return User.login(phone, pin, name, token)
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
            serializer = MultiUserTokenSerializer(
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
            if serializer.is_valid():
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
