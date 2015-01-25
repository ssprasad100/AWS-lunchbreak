from lunch.models import Store, DefaultFood, Food, StoreCategory, DefaultIngredient, Ingredient, IngredientGroup, User, Token, DefaultFoodCategory, FoodCategory, Order, OrderedFood, OpeningHours, HolidayPeriod
from lunch.exceptions import DoesNotExist, CostCheckFailed, MinTimeExceeded, PastOrderDenied

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from datetime import timedelta


class StoreCategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = StoreCategory
		fields = ('id', 'name',)


class StoreSerializer(serializers.ModelSerializer):
	categories = StoreCategorySerializer(many=True, read_only=True)

	class Meta:
		model = Store
		fields = ('id', 'name', 'country', 'province', 'city', 'code', 'street', 'number', 'latitude', 'longitude', 'categories',)


class OpeningHoursSerializer(serializers.ModelSerializer):

	class Meta:
		model = OpeningHours
		fields = ('id', 'day', 'opening', 'closing',)


class HolidayPeriodSerializer(serializers.ModelSerializer):

	class Meta:
		model = HolidayPeriod
		fields = ('id', 'description', 'start', 'end', 'closed',)


class ShortIngredientSerializer(serializers.ModelSerializer):

	class Meta:
		model = Ingredient
		fields = ('id', 'name', 'cost',)


class DefaultIngredientSerializer(serializers.ModelSerializer):

	class Meta:
		model = DefaultIngredient
		fields = ('id', 'name', 'cost', 'icon',)


class IngredientSerializer(serializers.ModelSerializer):

	class Meta:
		model = Ingredient
		fields = ('id', 'name', 'store', 'icon',)


class IngredientGroupSerializer(serializers.ModelSerializer):
	ingredients = ShortIngredientSerializer(many=True)

	class Meta:
		model = IngredientGroup
		fields = ('id', 'name', 'maximum', 'ingredients',)


class DefaultFoodCategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = DefaultFoodCategory
		fields = ('id', 'name', 'priority',)


class FoodCategorySerializer(DefaultFoodCategorySerializer):

	class Meta:
		model = FoodCategory
		fields = DefaultFoodCategorySerializer.Meta.fields + ('store',)


class DefaultFoodSerializer(serializers.ModelSerializer):
	ingredientGroups = IngredientGroupSerializer(many=True)
	category = DefaultFoodCategorySerializer(many=False)

	class Meta:
		model = DefaultFood
		fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'category', 'foodType',)


class FoodSerializer(serializers.ModelSerializer):
	ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
	category = FoodCategorySerializer(many=False)

	def create(self, validated_data):
		ingredients = Ingredient.objects.filter(id__in=validated_data['ingredients'])
		return Food(name=validated_data['name'], cost=validated_data['cost'], ingredients=ingredients, store=validated_data['store'], category=validated_data['category'], icon=validated_data['icon'])

	class Meta:
		model = Food
		fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'store', 'category', 'foodType',)
		read_only_fields = ('id', 'ingredientGroups',)


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


class UserSerializer(serializers.ModelSerializer):
	pin = serializers.CharField(required=False)
	device = serializers.CharField(required=False)

	class Meta:
		model = User
		fields = ('id', 'name', 'phone', 'pin', 'device',)
		write_only_fields = ('name', 'phone', 'pin', 'device',)


class ShortOrderSerializer(serializers.ModelSerializer):
	storeId = serializers.IntegerField(write_only=True)
	food = OrderedFoodSerializer(many=True, write_only=True, read_only=False)
	costCheck = serializers.DecimalField(decimal_places=2, max_digits=5, write_only=True)

	def create(self, validated_data):
		try:
			pickupTime = validated_data['pickupTime']

			if pickupTime < timezone.now():
				raise PastOrderDenied()

			store = Store.objects.get(id=validated_data['storeId'])

			if pickupTime - timezone.now() < timedelta(minutes=store.minTime):
				raise MinTimeExceeded()

			user = self.context['user']
			costCheck = validated_data['costCheck']

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

			if order.total != costCheck:
				order.delete()
				raise CostCheckFailed()

			return order
		except ObjectDoesNotExist:
			raise DoesNotExist('Store does not exist')

	class Meta:
		model = Order
		fields = ('id', 'storeId', 'pickupTime', 'paid', 'food', 'costCheck')
		read_only_fields = ('id', 'paid',)
		write_only_fields = ('storeId', 'costCheck', 'food', 'pickupTime',)


class OrderSerializer(ShortOrderSerializer):
	store = StoreSerializer(read_only=True)
	food = OrderedFoodSerializer(many=True, read_only=True, write_only=False)

	class Meta:
		model = Order
		fields = ShortOrderSerializer.Meta.fields + ('store', 'total', 'status', 'orderedTime',)
		read_only_fields = ShortOrderSerializer.Meta.read_only_fields + ('store', 'food', 'total', 'status', 'orderedTime',)
		write_only_fields = ('storeId', 'costCheck')


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
