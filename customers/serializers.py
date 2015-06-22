from customers.exceptions import AmountInvalid, CostCheckFailed
from customers.models import Order, OrderedFood, User, UserToken
from lunch.exceptions import BadRequest
from lunch.models import (INPUT_AMOUNT, INPUT_MIX, INPUT_WEIGHT, Food,
                          IngredientGroup, Store)
from lunch.serializers import (IngredientGroupSerializer, StoreSerializer,
                               TokenSerializer)
from rest_framework import serializers


class StoreHeartSerializer(StoreSerializer):
    hearted = serializers.BooleanField()

    class Meta:
        model = Store
        fields = StoreSerializer.Meta.fields + ('hearted',)
        read_only_fields = StoreSerializer.Meta.fields + ('hearted',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)

    class Meta:
        model = OrderedFood
        fields = ('id', 'ingredients', 'amount', 'unitAmount', 'order', 'original', 'ingredientGroups', 'cost', 'useOriginal',)
        read_only_fields = ('id', 'order', 'ingredientGroups', 'useOriginal',)


class OrderedFoodPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedFood
        fields = ('ingredients', 'amount', 'unitAmount', 'original',)
        write_only_fields = fields


class ShortOrderSerializer(serializers.ModelSerializer):
    '''
    Used after placing an order for confirmation.
    '''

    orderedFood = OrderedFoodSerializer(many=True, write_only=True)

    def costCheck(self, inputType, calculatedCost, amount, unitAmount, givenCost):
        if inputType == INPUT_AMOUNT and calculatedCost * amount != givenCost:
            raise CostCheckFailed()
        if inputType == INPUT_WEIGHT and calculatedCost * unitAmount != givenCost:
            raise CostCheckFailed()
        if inputType == INPUT_MIX and calculatedCost * unitAmount * amount != givenCost:
            raise CostCheckFailed()

    def amountCheck(self, inputType, amount, unitAmount):
        if inputType == INPUT_AMOUNT and (amount == 0 or unitAmount is not None):
            raise AmountInvalid()
        if inputType == INPUT_WEIGHT and (amount != 1 or unitAmount is None or unitAmount <= 0):
            raise AmountInvalid()
        if inputType == INPUT_MIX and (amount == 0 or unitAmount is None or unitAmount <= 0):
            raise AmountInvalid()

    def create(self, validated_data):
        pickupTime = validated_data['pickupTime']
        orderedFood = validated_data['orderedFood']
        store = validated_data['store']

        if len(orderedFood) == 0:
            raise BadRequest('orderedFood empty.')

        Store.checkOpen(store, pickupTime)

        user = self.context['user']

        order = Order(user=user, store=store, pickupTime=pickupTime)
        order.save()

        try:
            for f in orderedFood:
                original = f['original']
                amount = f['amount'] if 'amount' in f else 1
                unitAmount = f['unitAmount'] if 'unitAmount' in f else None
                inputType = original.foodType.inputType
                self.amountCheck(inputType, amount, unitAmount)
                cost = f['cost']

                orderedF = OrderedFood(original=original, order=order, amount=amount, cost=cost)

                if 'ingredients' in f:
                    orderedF.save()
                    ingredients = f['ingredients']
                    closestFood = Food.objects.closestFood(ingredients, original)
                    IngredientGroup.checkIngredients(ingredients, closestFood)
                    calculatedCost = OrderedFood.calculateCost(ingredients, closestFood)
                    self.costCheck(inputType, calculatedCost, amount, unitAmount, cost)
                    orderedF.cost = calculatedCost
                    orderedF.ingredients = ingredients
                else:
                    self.costCheck(inputType, original.cost, amount, unitAmount, cost)
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
        fields = ('id', 'store', 'pickupTime', 'paid', 'total', 'orderedFood', 'status',)
        read_only_fields = ('id', 'paid', 'total', 'status',)


class OrderSerializer(serializers.ModelSerializer):
    '''
    Used for listing a specific or all orders.
    '''

    store = StoreSerializer(read_only=True)
    orderedfood = OrderedFoodSerializer(many=True, read_only=True, source='orderedfood_set')

    class Meta:
        model = Order
        fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'orderedfood',)
        read_only_fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'orderedfood',)


class UserSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(required=False, write_only=True)
    device = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'phone', 'pin', 'device',)
        read_only_fields = ('id',)
        write_only_fields = ('phone', 'pin', 'device',)


class UserTokenSerializer(TokenSerializer):
    user = UserSerializer()

    class Meta:
        model = UserToken
        fields = TokenSerializer.Meta.fields + ('user',)
        read_only_fields = TokenSerializer.Meta.read_only_fields + ('user',)
