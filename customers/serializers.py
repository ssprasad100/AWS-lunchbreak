import math

from customers.exceptions import AmountInvalid, CostCheckFailed
from customers.models import Order, OrderedFood, User, UserToken
from lunch.config import INPUT_SI_SET, INPUT_SI_VARIABLE
from lunch.exceptions import BadRequest
from lunch.models import Food, IngredientGroup, Store
from lunch import serializers as lunchSerializers
from rest_framework import serializers


class StoreHeartSerializer(lunchSerializers.StoreSerializer):
    hearted = serializers.BooleanField()

    class Meta:
        model = Store
        fields = lunchSerializers.StoreSerializer.Meta.fields + ('hearted',)
        read_only_fields = lunchSerializers.StoreSerializer.Meta.fields + ('hearted',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = lunchSerializers.IngredientGroupSerializer(many=True, read_only=True)

    class Meta:
        model = OrderedFood
        fields = ('id', 'ingredients', 'amount', 'foodAmount', 'order', 'original', 'ingredientGroups', 'cost', 'useOriginal',)
        read_only_fields = ('id', 'foodAmount', 'order', 'ingredientGroups', 'useOriginal',)


class OrderedFoodPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedFood
        fields = ('ingredients', 'amount', 'original',)
        write_only_fields = fields


class SingleFoodSerializer(lunchSerializers.ShortSingleFoodSerializer):

    class Meta:
        model = lunchSerializers.ShortSingleFoodSerializer.Meta.model
        fields = ('id', 'name', 'description', 'amount', 'cost', 'ingredientGroups', 'ingredients', 'category', 'foodType', 'store', 'quantity', 'store',)
        read_only_fields = ('id', 'ingredientGroups',)


class ShortOrderSerializer(serializers.ModelSerializer):
    '''Used after placing an order for confirmation.'''

    orderedFood = OrderedFoodSerializer(many=True, write_only=True)

    def costCheck(self, calculatedCost, food, amount, givenCost):
        if math.ceil((calculatedCost * amount * (food.amount if food.foodType.inputType == INPUT_SI_SET else 1)) * 100) / 100.0 != float(givenCost):
            raise CostCheckFailed()

    def amountCheck(self, food, amount):
        if amount <= 0 \
            or (not float(amount).is_integer() and food.foodType.inputType != INPUT_SI_VARIABLE) \
            or (food.quantity is not None and not food.quantity.amountMin <= amount <= food.quantity.amountMax):
            raise AmountInvalid()

    def create(self, validated_data):
        pickupTime = validated_data['pickupTime']
        orderedFood = validated_data['orderedFood']
        store = validated_data['store']
        description = validated_data.get('description', None)

        if len(orderedFood) == 0:
            raise BadRequest('orderedFood empty.')

        Store.checkOpen(store, pickupTime)

        user = self.context['user']

        order = Order(user=user, store=store, pickupTime=pickupTime, description=description)
        order.save()

        try:
            for f in orderedFood:
                original = f['original']
                amount = f['amount'] if 'amount' in f else 1
                self.amountCheck(original, amount)
                cost = f['cost']
                foodAmount = original.amount if original.foodType.inputType == INPUT_SI_SET else 1

                orderedF = OrderedFood(amount=amount, foodAmount=foodAmount, cost=cost, order=order, original=original)

                if 'ingredients' in f:
                    orderedF.save()
                    ingredients = f['ingredients']

                    closestFood = Food.objects.closestFood(ingredients, original)
                    self.amountCheck(closestFood, amount)
                    IngredientGroup.checkIngredients(ingredients, closestFood)
                    calculatedCost = OrderedFood.calculateCost(ingredients, closestFood)
                    self.costCheck(calculatedCost, closestFood, amount, cost)

                    orderedF.cost = calculatedCost
                    orderedF.ingredients = ingredients
                else:
                    self.costCheck(original.cost, original, amount, cost)
                    orderedF.cost = original.cost
                    orderedF.useOriginal = True

                orderedF.save()
        except:
            order.delete()
            raise

        order.save()
        return order

    class Meta:
        model = Order
        fields = ('id', 'store', 'pickupTime', 'paid', 'total', 'orderedFood', 'status', 'description',)
        read_only_fields = ('id', 'paid', 'total', 'status',)
        write_only_fields = ('description',)


class OrderSerializer(serializers.ModelSerializer):
    '''Used for listing a specific or all orders.'''

    store = lunchSerializers.StoreSerializer(read_only=True)
    orderedfood = OrderedFoodSerializer(many=True, read_only=True, source='orderedfood_set')

    class Meta:
        model = Order
        fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'orderedfood', 'description',)
        read_only_fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'orderedfood', 'description',)


class UserSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(required=False, write_only=True)
    device = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'phone', 'pin', 'device',)
        read_only_fields = ('id',)
        write_only_fields = ('phone', 'pin', 'device',)


class UserTokenSerializer(lunchSerializers.TokenSerializer):
    user = UserSerializer()

    class Meta:
        model = UserToken
        fields = lunchSerializers.TokenSerializer.Meta.fields + ('user',)
        read_only_fields = lunchSerializers.TokenSerializer.Meta.read_only_fields + ('user',)
