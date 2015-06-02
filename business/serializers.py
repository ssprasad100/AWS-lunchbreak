from business.models import Employee, EmployeeToken, Staff, StaffToken
from customers.models import Order, OrderedFood, User
from lunch.exceptions import InvalidStoreLinking
from lunch.models import (Food, FoodCategory, Ingredient, IngredientGroup,
                          IngredientRelation)
from lunch.serializers import (DefaultFoodSerializer,
                               FoodSerializer,
                               ShortDefaultIngredientRelationSerializer,
                               StoreSerializer, TokenSerializer, DefaultFoodCategorySerializer)
from rest_framework import serializers


class BusinessTokenSerializer(TokenSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    device = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        fields = TokenSerializer.Meta.fields + ('password', 'device',)
        write_only_fields = ('password', 'device',)
        read_only_fields = ()


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'store', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class StaffTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + ('staff',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'name', 'password', 'owner',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + ('employee',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields


class PrivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        model = OrderedFood
        fields = ('id', 'ingredients', 'amount', 'original', 'cost', 'useOriginal',)
        read_only_fields = fields


class ShortOrderSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'orderedTime', 'pickupTime', 'status', 'paid', 'total',)
        read_only_fields = ('id', 'user', 'orderedTime', 'pickupTime', 'paid', 'total',)


class OrderSerializer(ShortOrderSerializer):
    orderedFood = OrderedFoodSerializer(many=True, read_only=True, source='orderedfood_set')

    class Meta:
        model = Order
        fields = ShortOrderSerializer.Meta.fields + ('orderedFood',)
        read_only_fields = ShortOrderSerializer.Meta.read_only_fields + ('orderedFood',)


class ShortIngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'minimum', 'priority', 'cost', 'foodType',)
        read_only_fields = ('id',)


class IngredientRelationSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRelation
        fields = ('ingredient', 'typical',)
        write_only_fields = fields


class FoodCategorySerializer(DefaultFoodCategorySerializer):

    class Meta:
        model = FoodCategory
        fields = DefaultFoodCategorySerializer.Meta.fields
        read_only_fields = DefaultFoodCategorySerializer.Meta.read_only_fields


class ShortFoodSerializer(serializers.ModelSerializer):
    ingredients = ShortDefaultIngredientRelationSerializer(source='ingredientrelation_set', many=True, required=False, read_only=True)
    ingredientRelations = IngredientRelationSerializer(source='ingredientrelation_set', many=True, required=False, write_only=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'category', 'foodType', 'cost', 'ingredients', 'category', 'ingredientRelations',)
        read_only_fields = ('id', 'ingredients',)
        write_only_fields = ('ingredientRelations',)

    def createOrUpdate(self, validated_data, food=None):
        update = food is not None
        if not update:
            name = validated_data['name']
            category = validated_data['category']
            foodType = validated_data['foodType']
            cost = validated_data['cost']
            store = validated_data['store']

            food = Food(name=name, category=category, foodType=foodType, cost=cost, store=store)
        else:
            food.name = validated_data.get('name', food.name)
            food.category = validated_data.get('category', food.category)
            food.foodType = validated_data.get('foodType', food.foodType)
            food.cost = validated_data.get('cost', food.cost)
            food.store = validated_data.get('store', food.store)

        relations = validated_data.get('ingredientrelation_set', None)
        if relations is not None:
            for relation in relations:
                if relation['ingredient'].store_id != food.store.id:
                    raise InvalidStoreLinking()

        food.save()

        if relations is not None:
            if update:
                IngredientRelation.objects.filter(food=food).delete()
            for relation in relations:
                IngredientRelation.objects.update_or_create(food=food, **relation)

        return food

    def create(self, validated_data):
        return self.createOrUpdate(validated_data)

    def update(self, instance, validated_data):
        return self.createOrUpdate(validated_data, instance)


class StoreFoodSerializer(FoodSerializer):
    class Meta:
        model = Food
        fields = DefaultFoodSerializer.Meta.fields
        read_only_fields = DefaultFoodSerializer.Meta.read_only_fields


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'cost', 'icon', 'group',)
        read_only_fields = ('id',)


class IngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'minimum', 'ingredients', 'priority', 'cost', 'foodType',)
        read_only_fields = ('id', 'ingredients',)
