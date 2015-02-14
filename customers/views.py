import datetime

from customers.authentication import LunchbreakAuthentication
from customers.models import Order, OrderedFood, Token, tokenGenerator, User
from customers.serializers import (OrderedFoodPriceSerializer, OrderSerializer,
									ShortOrderSerializer, TokenSerializer,
									UserSerializer)
from django.utils import timezone
from customers.digits import Digits
from lunch.exceptions import BadRequest
from lunch.models import Food, HolidayPeriod, Ingredient, OpeningHours, Store
from lunch.serializers import (FoodSerializer, HolidayPeriodSerializer,
								OpeningHoursSerializer, StoreSerializer)
from rest_framework import generics, status
from rest_framework.response import Response


class StoreListView(generics.ListAPIView):
	'''
	List the stores.
	'''

	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = StoreSerializer

	def get_queryset(self):
		proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
		if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
			return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
		elif 'id' in self.kwargs:
			return Store.objects.filter(id=self.kwargs['id'])


class OpeningHoursListView(generics.ListAPIView):
	'''
	List the opening hours of a store.
	'''

	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = OpeningHoursSerializer

	def get_queryset(self):
		return OpeningHours.objects.filter(store_id=self.kwargs['store_id']).order_by('day', 'opening')


class HolidayPeriodListView(generics.ListAPIView):
	'''
	List the opening hours of a store.
	'''

	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = HolidayPeriodSerializer

	def get_queryset(self):
		return HolidayPeriod.objects.filter(store_id=1, start__lte=timezone.now() + datetime.timedelta(days=7), end__gte=timezone.now())


class FoodListView(generics.ListAPIView):
	'''
	List the available food.
	'''

	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = FoodSerializer

	def get_queryset(self):
		if 'store_id' in self.kwargs:
			return Food.objects.filter(store_id=self.kwargs['store_id'])
		elif 'id' in self.kwargs:
			return Food.objects.filter(id=self.kwargs['id'])


class OrderView(generics.ListCreateAPIView):
	'''
	Order food.
	'''

	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = OrderSerializer

	def get_queryset(self):
		'''
		Return all of the Orders for the authenticated user.
		'''
		if 'id' in self.kwargs:
			return Order.objects.filter(user=self.request.user, id=self.kwargs['id'])
		return Order.objects.filter(user=self.request.user)

	def create(self, request, *args, **kwargs):
		orderSerializer = ShortOrderSerializer(data=request.data, context={'user': request.user})
		if orderSerializer.is_valid():
			orderSerializer.save()
			return Response(data=orderSerializer.data, status=status.HTTP_201_CREATED)
		raise BadRequest(orderSerializer.errors)


class OrderPriceView(generics.CreateAPIView):
	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = OrderedFoodPriceSerializer

	def post(self, request, format=None):
		'''
		Return the price of the food.
		'''
		priceSerializer = OrderedFoodPriceSerializer(data=request.data, many=True)
		if priceSerializer.is_valid():
			costList = []
			for priceCheck in priceSerializer.validated_data:
				exact, closestFood = OrderedFood.objects.closestFood(orderedFood=None, ingredients=priceCheck['ingredients'], storeId=priceCheck['store'])
				if not exact:
					orderedIngredients = Ingredient.objects.filter(id__in=priceCheck['ingredients'], store_id=priceCheck['store'])
					cost = OrderedFood.calculateCost(orderedIngredients, closestFood)
				else:
					cost = closestFood.cost
				costList.append(cost)
			return Response(data=costList, status=status.HTTP_200_OK)
		raise BadRequest(priceSerializer.errors)


class TokenView(generics.ListAPIView):
	'''
	Tokens can only be listed (for now).
	'''

	authentication_classes = (LunchbreakAuthentication,)
	serializer_class = TokenSerializer

	def get_queryset(self):
		'''
		Return all of the Tokens for the authenticated user.
		'''
		return Token.objects.filter(user=self.request.user)


class UserView(generics.CreateAPIView):

	serializer_class = UserSerializer

	# For all these methods a try-except is not needed since a DigitsException is generated
	# which will provide everything
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
							user.confirmedAt = datetime.now()

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
							token, created = Token.objects.get_or_create(device=device, user=user)
							if not created:
								token.identifier = tokenGenerator()
							token.save()
							tokenSerializer = TokenSerializer(token)
							data = dict(tokenSerializer.data)
							data['name'] = name
							return Response(data, status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK))
		raise BadRequest(userSerializer.errors)
