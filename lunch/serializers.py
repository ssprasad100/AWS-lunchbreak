from lunch.models import Store, DefaultFood, Food, StoreCategory, DefaultIngredient, Ingredient, IngredientGroup, User, Token, DefaultFoodCategory, FoodCategory, Order, OrderedFood
from lunch.exceptions import DoesNotExist

from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist


class StoreCategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = StoreCategory
		fields = ('id', 'name',)


class StoreSerializer(serializers.ModelSerializer):
	categories = StoreCategorySerializer(many=True, read_only=True)

	class Meta:
		model = Store
		fields = ('id', 'name', 'country', 'province', 'city', 'code', 'street', 'number', 'latitude', 'longitude', 'categories',)


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
		fields = ('id', 'name',)


class FoodCategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = FoodCategory
		fields = ('id', 'name', 'store',)


class DefaultFoodSerializer(serializers.ModelSerializer):
	ingredientGroups = IngredientGroupSerializer(many=True)
	category = DefaultFoodCategorySerializer(many=False)

	class Meta:
		model = DefaultFood
		fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'category', 'icon',)


class FoodSerializer(serializers.ModelSerializer):
	ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
	category = FoodCategorySerializer(many=False)

	def create(self, validated_data):
		ingredients = Ingredient.objects.filter(id__in=validated_data['ingredients'])
		return Food(name=validated_data['name'], cost=validated_data['cost'], ingredients=ingredients, store=validated_data['store'], category=validated_data['category'], icon=validated_data['icon'])

	class Meta:
		model = Food
		fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'store', 'category', 'icon',)
		read_only_fields = ('id', 'ingredientGroups',)


class OrderedFoodSerializer(FoodSerializer):
	category = FoodCategorySerializer(many=False, read_only=True)
	referenceId = serializers.IntegerField(write_only=True, required=False)

	def to_internal_value(self, data):
		# Name is temporary
		name = data.get('name')
		ingredients = data.get('ingredients')
		referenceId = data.get('referenceId')

		if not ingredients and not referenceId:
			raise serializers.ValidationError({
				'ingredients, referenceId': 'One of these fields is required.'
			})

		if not name:
			raise serializers.ValidationError({
				'name': 'This field is required.'
			})

		result = {
			'name': name
		}

		if ingredients:
			result['ingredients'] = ingredients

		if referenceId:
			result['referenceId'] = referenceId

		return result

	class Meta:
		model = OrderedFood
		read_only_fields = ('id', 'cost', 'ingredientGroups', 'store', 'category', 'icon',)
		write_only_fields = ('referenceId',)


class UserSerializer(serializers.ModelSerializer):
	pin = serializers.CharField()
	device = serializers.CharField()

	def to_internal_value(self, data):
		phone = data.get('phone')

		if not phone:
			raise serializers.ValidationError({
				'phone': 'This field is required.'
			})

		# TODO Check whether the phone number is a valid phone number
		return {
			'phone': phone
		}

	class Meta:
		model = User
		fields = ('name', 'phone', 'pin', 'device',)
		write_only_fields = ('name', 'phone', 'pin', 'device',)


class OrderSerializer(serializers.ModelSerializer):
	store = StoreSerializer(read_only=True)
	storeId = serializers.IntegerField(write_only=True)
	food = OrderedFoodSerializer(many=True)

	def create(self, validated_data):
		try:
			user = self.context['user']
			store = Store.objects.get(id=validated_data['storeId'])

			food = []
			for f in validated_data['food']:
				print 'Creating orderedFood'
				orderedFood = OrderedFood()
				if 'referenceId' in f:
					referenceFood = Food.objects.filter(id=f['referenceId'])
					if len(referenceFood) == 0:
						raise DoesNotExist('Referenced food does not exist')
					orderedFood = OrderedFood(**referenceFood.values()[0])
				else:
					orderedFood.store = store
					orderedFood.name = f['name']
					# DEBUGGING PURPOSES ONLY
					orderedFood.cost = 0
					orderedFood.save()
					print 'Setting ingredients'
					orderedFood.ingredients = f['ingredients']
				orderedFood.save()
				food.append(orderedFood)
				print orderedFood

			order = Order(user=user, store=store, pickupTime=validated_data['pickupTime'])
			order.save()
			order.food = food
			order.save()

			return order
		except ObjectDoesNotExist:
			raise DoesNotExist('Store does not exist')

	class Meta:
		model = Order
		fields = ('store', 'storeId', 'orderedTime', 'pickupTime', 'status', 'paid', 'food',)
		read_only_fields = ('store', 'orderedTime', 'status', 'paid',)
		write_only_fields = ('storeId',)


class TokenUserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('userId',)


class TokenSerializer(serializers.ModelSerializer):
	user = TokenUserSerializer()

	def to_representation(self, obj):
		return {
			'id': obj.id,
			'identifier': obj.identifier,
			'device': obj.device,
			'user': obj.user.userId,
		}

	class Meta:
		model = Token
		fields = ('id', 'identifier', 'device', 'user',)
		read_only_fields = ('id', 'identifier', 'user',)
