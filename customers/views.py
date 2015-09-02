from customers.authentication import CustomerAuthentication
from customers.config import DEMO_DIGITS_ID, DEMO_PHONE
from customers.digits import Digits
from customers.models import Heart, Order, OrderedFood, User, UserToken
from customers.serializers import (OrderedFoodPriceSerializer, OrderSerializer,
                                   OrderSerializerOld, ShortOrderSerializer,
                                   ShortOrderSerializerOld,
                                   StoreHeartSerializer, UserLoginSerializer,
                                   UserRegisterSerializer, UserSerializer,
                                   UserTokenSerializer,
                                   UserTokenUpdateSerializer)
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lunch.models import Food, FoodCategory, IngredientGroup, Store
from lunch.pagination import SimplePagination
from lunch.responses import BadRequest
from lunch.serializers import (FoodCategorySerializer, HolidayPeriodSerializer,
                               MultiFoodSerializer, OpeningHoursSerializer,
                               OpenSerializer, ShortFoodCategorySerializer,
                               ShortStoreSerializer, SingleFoodSerializer)
from lunch.views import (StoreCategoryListViewBase, getHolidayPeriods,
                         getOpeningAndHoliday, getOpeningHours)
from Lunchbreak.exceptions import LunchbreakException
from rest_framework import generics, status
from rest_framework.response import Response


class StoreMultiView(generics.ListAPIView):
    '''List the stores.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortStoreSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
        else:
            return Store.objects.filter(order__user=self.request.user).order_by('-order__orderedTime').distinct()


class StoreHeartView(generics.RetrieveUpdateAPIView):
    '''Heart or unheart a store.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = StoreHeartSerializer
    queryset = Store.objects.all()

    def get(self, request, pk, **kwargs):
        store = get_object_or_404(Store, id=pk)
        store.hearted = request.user in store.hearts.all()
        serializer = self.serializer_class(store)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk, **kwargs):
        heart = 'option' in self.kwargs and self.kwargs['option'] == 'heart'
        store = get_object_or_404(Store, id=pk)

        if heart:
            heart, created = Heart.objects.get_or_create(store=store, user=request.user)
            statusCode = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(status=statusCode)
        else:
            heart = get_object_or_404(Heart, store=store, user=request.user)
            heart.delete()
            return Response(status=status.HTTP_200_OK)


class StoreOpenView(generics.ListAPIView):
    '''List the opening hours and holiday periods of a store.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = OpenSerializer
    pagination_class = None
    queryset = None

    def get(self, request, *args, **kwargs):
        return getOpeningAndHoliday(self.kwargs['store_id'])


class StoreCategoryListView(StoreCategoryListViewBase):
    authentication_classes = (CustomerAuthentication,)


class OpeningHoursListView(generics.ListAPIView):
    '''List the opening hours of a store.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = OpeningHoursSerializer
    pagination_class = None

    def get_queryset(self):
        return getOpeningHours(self.kwargs['store_id'])


class HolidayPeriodListView(generics.ListAPIView):
    '''List the holiday periods of a store.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = HolidayPeriodSerializer
    pagination_class = None

    def get_queryset(self):
        return getHolidayPeriods(self.kwargs['store_id'])


class FoodListView(generics.ListAPIView):
    '''List the available food.'''

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
        return result.order_by(
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


class FoodRetrieveView(generics.RetrieveAPIView):
    '''Retrieve a specific food.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = SingleFoodSerializer

    def get_queryset(self):
        return Food.objects.filter(deleted=False)


class FoodCategoryListView(generics.ListAPIView):
    ''' List all food categories. '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = ShortFoodCategorySerializer
    pagination_class = None

    def get_queryset(self):
        if 'store_id' in self.kwargs:
            return FoodCategory.objects.filter(
                store_id=self.kwargs['store_id']
            ).order_by('-priority', 'name')


class FoodCategoryRetrieveView(generics.RetrieveAPIView):
    ''' List all food categories. '''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.all()


class OrderView(generics.ListCreateAPIView):
    '''Place an order and list a specific or all of the user's orders.'''

    authentication_classes = (CustomerAuthentication,)

    def get_serializer_class(self):
        if self.request.version > 1:
            return ShortOrderSerializer
        else:
            return ShortOrderSerializerOld

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-pickupTime')

    def create(self, request, *args, **kwargs):
        serializerClass = self.get_serializer_class()
        orderSerializer = serializerClass(data=request.data, context={'user': request.user})
        if orderSerializer.is_valid():
            try:
                orderSerializer.save()
            except LunchbreakException as e:
                return e.getResponse()
            else:
                return Response(data=orderSerializer.data, status=status.HTTP_201_CREATED)
        return BadRequest(orderSerializer.errors)


class OrderRetrieveView(generics.RetrieveAPIView):
    '''Retrieve a single order.'''

    authentication_classes = (CustomerAuthentication,)
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.version > 1:
            return OrderSerializer
        else:
            return OrderSerializerOld


class OrderPriceView(generics.CreateAPIView):
    authentication_classes = (CustomerAuthentication,)
    serializer_class = OrderedFoodPriceSerializer

    def post(self, request, format=None):
        '''Return the price of the food.'''
        priceSerializer = OrderedFoodPriceSerializer(data=request.data, many=True)
        if priceSerializer.is_valid():
            result = []
            for priceCheck in priceSerializer.validated_data:
                priceInfo = {}
                original = priceCheck['original']
                if 'ingredients' in priceCheck:
                    ingredients = priceCheck['ingredients']
                    closestFood = Food.objects.closestFood(ingredients, original)
                    IngredientGroup.checkIngredients(ingredients, closestFood)

                    priceInfo['cost'] = OrderedFood.calculateCost(ingredients, closestFood)
                    priceInfo['food'] = closestFood.id
                else:
                    priceInfo['cost'] = original.cost
                    priceInfo['food'] = original.id
                result.append(priceInfo)
            return Response(data=result, status=status.HTTP_200_OK)
        return BadRequest(priceSerializer.errors)


class UserTokenView(generics.ListAPIView):
    '''Return all of the Tokens for the authenticated user.'''

    authentication_classes = (CustomerAuthentication,)
    serializer_class = UserTokenSerializer

    def get_queryset(self):
        return UserToken.objects.filter(user=self.request.user)


class UserRegisterView(generics.CreateAPIView):

    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        registerSerializer = UserRegisterView.serializer_class(data=request.data)
        phone = request.data.get('phone', False)
        if registerSerializer.is_valid():
            return User.register(phone)
        elif phone == DEMO_PHONE:
            return Response(status=status.HTTP_200_OK)
        return BadRequest(registerSerializer.errors)


class UserLoginView(generics.CreateAPIView):

    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        loginSerializer = UserLoginView.serializer_class(data=request.data)
        phone = request.data.get('phone', False)
        if loginSerializer.is_valid():
            pin = request.data['pin']
            name = request.data.get('name', None)
            token = request.data.get('token', None)
            return User.login(phone, pin, name, token)
        elif (phone == DEMO_PHONE
            and 'token' in request.data
            and 'device' in request.data['token']
            and 'pin' in request.data):
            try:
                demoUser = User.objects.get(
                    phone=phone,
                    requestId=request.data['pin'],
                    digitsId=DEMO_DIGITS_ID
                )
                return UserView.createGetToken(demoUser, request.data['token']['device'])
            except User.DoesNotExist:
                pass
        return BadRequest(loginSerializer.errors)


class UserTokenUpdateView(generics.UpdateAPIView):

    serializer_class = UserTokenUpdateSerializer
    authentication_classes = (CustomerAuthentication,)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.auth.registration_id = request.data['registration_id']
            request.auth.save()
            return Response(
                self.serializer_class(request.auth).data,
                status=status.HTTP_200_OK
            )
        return BadRequest(serializer.errors)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class UserView(generics.CreateAPIView):

    serializer_class = UserSerializer

    # For all these methods a try-except is not needed since a DigitsException is generated which will provide everything
    def register(self, digits, phone):
        try:
            digits.register(phone)
            return True
        except:
            return self.signIn(digits, phone)

    def signIn(self, digits, phone):
        content = digits.signin(phone)
        return {
            'digitsId': content['login_verification_user_id'],
            'requestId': content['login_verification_request_id']
        }

    def confirmRegistration(self, digits, phone, pin):
        content = digits.confirmRegistration(phone, pin)
        return content['id']

    def confirmSignin(self, digits, requestId, digitsId, pin):
        digits.confirmSignin(requestId, digitsId, pin)
        return True

    def getRegistrationResponse(self, hasName=False):
        if hasName:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def createGetToken(user, device):
        token, created = UserToken.objects.createToken(user, device)
        tokenSerializer = UserTokenSerializer(token)
        return Response(tokenSerializer.data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))

    def create(self, request, *args, **kwargs):
        userSerializer = UserSerializer(data=request.data)
        if userSerializer.is_valid():
            phone = request.data.__getitem__('phone')
            queryset = User.objects.filter(phone=phone)
            digits = Digits()
            if not queryset:
                result = self.register(digits, phone)
                if result:
                    user = User(phone=phone)
                    if type(result) is dict:
                        user.digitsId = result['digitsId']
                        user.requestId = result['requestId']
                    user.save()
                    return self.getRegistrationResponse()
            else:
                pin = request.data.get('pin', False)
                user = queryset[0]
                hasName = user.name != ''
                givenName = request.data.get('name', False)
                name = givenName if givenName else user.name
                if not pin:
                    # The user is in the database, but isn't sending a pin code so he's trying to signin/register
                    if user.confirmedAt:
                        result = self.signIn(digits, phone)
                        if result:
                            user.digitsId = result['digitsId']
                            user.requestId = result['requestId']
                            user.save()
                            return self.getRegistrationResponse(hasName)
                    else:
                        result = self.register(digits, phone)
                        if result:
                            if type(result) is dict:
                                user.digitsId = result['digitsId']
                                user.requestId = result['requestId']
                            user.save()
                            return self.getRegistrationResponse(hasName)
                elif name:
                    device = request.data.get('device', False)
                    user.name = name
                    success = False
                    if device:
                        if not user.confirmedAt:
                            user.confirmedAt = timezone.now()

                        if not user.requestId and not user.digitsId:
                            # The user already got a message, but just got added to the Digits database
                            user.digitsId = self.confirmRegistration(digits, phone, pin)
                            user.save()
                            success = True
                        else:
                            # The user already was in the Digits database and got a request and user id
                            self.confirmSignin(digits, user.requestId, user.digitsId, pin)
                            user.save()
                            success = True

                        if success:
                            return UserView.createGetToken(user, device)
        elif request.data.get('phone', False) == DEMO_PHONE:
            if 'pin' not in request.data:
                return Response(status=status.HTTP_200_OK)

            if 'device' in request.data:
                try:
                    demoUser = User.objects.get(phone=request.data['phone'], requestId=request.data['pin'], digitsId='demo')
                except ObjectDoesNotExist:
                    pass
                else:
                    return UserView.createGetToken(demoUser, request.data['device'])
        return BadRequest(userSerializer.errors)
