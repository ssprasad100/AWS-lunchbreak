from lunch.models import Store, DefaultFood, Food, StoreCategory, DefaultIngredient, Ingredient, IngredientGroup, User, Token

from rest_framework import serializers


class StoreCategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = StoreCategory
		fields = ('id', 'name')


class StoreSerializer(serializers.ModelSerializer):
	categories = StoreCategorySerializer(many=True, read_only=True)

	class Meta:
		model = Store
		fields = ('id', 'name', 'country', 'province', 'city', 'code', 'street', 'number', 'latitude', 'longitude', 'categories')


class IngredientSerializer(serializers.ModelSerializer):

	class Meta:
		model = Ingredient
		fields = ('id', 'name', 'store')


class ShortIngredientSerializer(serializers.ModelSerializer):

	class Meta:
		model = Ingredient
		fields = ('id', 'name', 'cost')


class DefaultIngredientSerializer(serializers.ModelSerializer):

	class Meta:
		model = DefaultIngredient
		fields = ('id', 'name', 'cost')


class IngredientGroupSerializer(serializers.ModelSerializer):
	ingredients = ShortIngredientSerializer(many=True)

	class Meta:
		model = IngredientGroup
		fields = ('id', 'name', 'maximum', 'ingredients')


class DefaultFoodSerializer(serializers.ModelSerializer):
	ingredientGroups = IngredientGroupSerializer(many=True)

	class Meta:
		model = DefaultFood
		fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients')


class FoodSerializer(serializers.ModelSerializer):
	ingredientGroups = IngredientGroupSerializer(many=True)

	class Meta:
		model = Food
		fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'store')


class UserSerializer(serializers.ModelSerializer):
	pin = serializers.CharField()
	device = serializers.CharField()

	def to_internal_value(self, data):
		phone = data.get('phone')

		if not phone:
			raise serializers.ValidationError({
				'phone': 'This field is required'
			})

		# TODO Check whether the phone number is a valid phone number
		return {
			'phone': phone
		}

	class Meta:
		model = User
		fields = ('name', 'phone', 'pin', 'device')
		write_only_fields = ('name', 'phone', 'pin', 'device')


class TokenUserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('userId')


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
		fields = ('id', 'identifier', 'device', 'user')
		read_only_fields = ('id', 'identifier', 'user')
