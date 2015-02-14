from customers.models import Order, OrderedFood, User, Token

from lunch.models import Store, Food, Ingredient
from lunch.exceptions import DoesNotExist, MinTimeExceeded, PastOrderDenied
from lunch.serializers import FoodSerializer, FoodCategorySerializer, StoreSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from datetime import timedelta


class OrderedFoodSerializer(FoodSerializer):
	category = FoodCategorySerializer(many=False, read_only=True)
	referenceId = serializers.IntegerField(write_only=True, required=False)
	amount = serializers.IntegerField(required=False)

	def to_internal_value(self, data):
		if 'referenceId' not in data and 'ingredients' not in data:
			raise serializers.ValidationError({'referenceId, ingredients': 'One of these fields is required.'})
		return super(OrderedFoodSerializer, self).to_internal_value(data)

	class Meta:
		model = OrderedFood
		fields = FoodSerializer.Meta.fields + ('referenceId', 'amount',)
		read_only_fields = ('id', 'cost', 'ingredientGroups', 'store', 'category', 'foodType',)
		write_only_fields = ('referenceId',)


class OrderedFoodPriceSerializer(serializers.BaseSerializer):
	ingredients = serializers.ListField(child=serializers.IntegerField())
	store = serializers.IntegerField()

	def to_internal_value(self, data):
		store = data.get('store')
		ingredients = data.get('ingredients')

		# Perform the data validation.
		if not store:
			raise ValidationError({
				'store': 'This field is required.'
			})
		elif len(Store.objects.filter(id=store)) == 0:
			raise ValidationError({
				'store': 'Store id does not exist.'
			})

		if not ingredients:
			raise ValidationError({
				'ingredients': 'This field is required.'
			})
		if type(ingredients) is not list:
			raise ValidationError({
				'ingredients': 'This field is needs to be a list of integers.'
			})

		return {
			'store': int(store),
			'ingredients': [int(i) for i in ingredients]
		}

	def to_representation(self, obj):
		return {
			'store': obj.store,
			'ingredients': obj.ingredients
		}

	class Meta:
		fields = ('ingredients', 'store',)


class ShortOrderSerializer(serializers.ModelSerializer):
	storeId = serializers.IntegerField(write_only=True)
	food = OrderedFoodSerializer(many=True, write_only=True, read_only=False)

	def create(self, validated_data):
		try:
			pickupTime = validated_data['pickupTime']

			if pickupTime < timezone.now():
				raise PastOrderDenied()

			store = Store.objects.get(id=validated_data['storeId'])

			if pickupTime - timezone.now() < timedelta(minutes=store.minTime):
				raise MinTimeExceeded()

			user = self.context['user']

			food = []
			for f in validated_data['food']:
				orderedFood = OrderedFood()
				if 'referenceId' in f:
					referenceFood = Food.objects.filter(id=f['referenceId'])
					if len(referenceFood) == 0:
						raise DoesNotExist('Referenced food does not exist.')
					orderedFood = OrderedFood(**referenceFood.values()[0])
					orderedFood.pk = None
				else:
					orderedFood.store = store
					orderedFood.name = f['name']
					ingredientIds = [ingredient.id for ingredient in f['ingredients']]
					exact, closestFood = OrderedFood.objects.closestFood(orderedFood, ingredientIds)
					orderedFood.cost = closestFood.cost if exact else OrderedFood.calculateCost(Ingredient.objects.filter(id__in=ingredientIds, store_id=store), closestFood)
					orderedFood.save()
					orderedFood.ingredients = f['ingredients']

				orderedFood.amount = f['amount'] if 'amount' in f else 1
				orderedFood.save()
				food.append(orderedFood)

			order = Order(user=user, store=store, pickupTime=pickupTime)
			order.save()
			order.food = food
			order.save()

			return order
		except ObjectDoesNotExist:
			raise DoesNotExist('Store does not exist')

	class Meta:
		model = Order
		fields = ('id', 'storeId', 'pickupTime', 'paid', 'food',)
		read_only_fields = ('id', 'paid',)
		write_only_fields = ('storeId', 'food', 'pickupTime',)


class OrderSerializer(ShortOrderSerializer):
	store = StoreSerializer(read_only=True)
	food = OrderedFoodSerializer(many=True, read_only=True, write_only=False)

	class Meta:
		model = Order
		fields = ShortOrderSerializer.Meta.fields + ('store', 'total', 'status', 'orderedTime',)
		read_only_fields = ShortOrderSerializer.Meta.read_only_fields + ('store', 'food', 'total', 'status', 'orderedTime',)
		write_only_fields = ('storeId',)


class UserSerializer(serializers.ModelSerializer):
	pin = serializers.CharField(required=False)
	device = serializers.CharField(required=False)

	class Meta:
		model = User
		fields = ('id', 'name', 'phone', 'pin', 'device',)
		write_only_fields = ('name', 'phone', 'pin', 'device',)


class TokenUserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('id',)


class TokenSerializer(serializers.ModelSerializer):
	user = TokenUserSerializer()

	def to_representation(self, obj):
		return {
			'id': obj.id,
			'identifier': obj.identifier,
			'device': obj.device,
			'user': obj.user.id,
		}

	class Meta:
		model = Token
		fields = ('id', 'identifier', 'device', 'user',)
		read_only_fields = ('id', 'identifier', 'user',)
