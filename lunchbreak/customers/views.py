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
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import list_route
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


class FoodListView(generics.ListAPIView):

    """List the available food."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = MultiFoodSerializer

    def get_queryset(self):
        if 'store_id' in self.kwargs:
            result = Food.objects.filter(
                store_id=self.kwargs['store_id'],
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
    def pagination_class(self):
        if 'foodcategory_id' in self.kwargs:
            return None
        return SimplePagination


class FoodCategoryRetrieveView(generics.RetrieveAPIView):

    """List all food categories."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.select_related(
        'store',
    ).all()


class OrderView(generics.ListCreateAPIView):

    """Place an order and list a specific or all of the user's orders."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortOrderSerializer

    def get_queryset(self):
        return Order.objects.select_related(
            'store',
        ).filter(
            user=self.request.user
        ).order_by(
            '-pickup'
        )


class OrderRetrieveView(generics.RetrieveAPIView):

    """Retrieve a single order."""

    authentication_classes = (CustomerAuthentication,)
    queryset = Order.objects.select_related(
        'store',
    ).all()
    serializer_class = OrderSerializer


class OrderPriceView(generics.CreateAPIView):
    authentication_classes = (CustomerAuthentication,)
    serializer_class = OrderedFoodPriceSerializer

    def post(self, request, format=None):
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


class ReservationSingleView(generics.RetrieveUpdateAPIView):

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        )


class StoreHeartView(generics.RetrieveUpdateAPIView):

    """Heart or unheart a store."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = StoreHeartSerializer
    queryset = Store.objects.all()

    def get(self, request, pk, **kwargs):
        store = get_object_or_404(Store, id=pk)
        store.hearted = request.user in store.hearts.all()
        serializer = self.get_serializer_class()(store)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk, **kwargs):
        heart = 'option' in self.kwargs and self.kwargs['option'] == 'heart'
        store = get_object_or_404(Store, id=pk)

        if heart:
            heart, created = Heart.objects.get_or_create(
                store=store,
                user=request.user
            )
            statusCode = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(status=statusCode)
        else:
            heart = get_object_or_404(
                Heart,
                store=store,
                user=request.user
            )
            heart.delete()
            return Response(status=status.HTTP_200_OK)


class OpeningHoursListView(OpeningHoursListViewBase):
    authentication_classes = (CustomerAuthentication,)


class HolidayPeriodListView(HolidayPeriodListViewBase):
    authentication_classes = (CustomerAuthentication,)


class StoreHoursView(OpeningListViewBase):
    authentication_classes = (CustomerAuthentication,)


class FoodCategoryListView(generics.ListAPIView):

    """ List all food categories. """

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortFoodCategorySerializer
    pagination_class = None

    def get_queryset(self):
        if 'store_id' in self.kwargs:
            return FoodCategory.objects.filter(
                store_id=self.kwargs['store_id']
            ).order_by(
                '-priority',
                'name'
            )


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


class StoreMultiView(generics.ListAPIView):

    """List the stores."""

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortStoreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'city', 'street',)

    def get_queryset(self):
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
            email = request.data.get('email', None)
            token = request.data.get('token', None)
            return User.login(phone, pin, name, email, token)
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
