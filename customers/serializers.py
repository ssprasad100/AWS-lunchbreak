from datetime import timedelta

from customers.exceptions import (CostCheckFailed, MinTimeExceeded,
                                  PastOrderDenied, StoreClosed)
from customers.models import Order, OrderedFood, User, UserToken
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from lunch.exceptions import DoesNotExist, BadRequest
from lunch.models import Food, Ingredient, Store, OpeningHours
from lunch.serializers import (FoodCategorySerializer, FoodSerializer,
                               FoodTypeSerializer, StoreSerializer,
                               TokenSerializer)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class ShortStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = ('id', 'name',)
        read_only_fields = ('name',)


class OrderedFoodSerializer(FoodSerializer):
    category = FoodCategorySerializer(many=False, read_only=True)
    referenceId = serializers.IntegerField(write_only=True, required=False)
    amount = serializers.IntegerField(required=False)
    foodType = FoodTypeSerializer(many=False, required=False)

    def to_internal_value(self, data):
        if 'referenceId' not in data and 'ingredients' not in data:
            raise serializers.ValidationError({'referenceId, ingredients': 'One of these fields is required.'})
        return super(OrderedFoodSerializer, self).to_internal_value(data)

    class Meta:
        model = OrderedFood
        fields = FoodSerializer.Meta.fields + ('referenceId', 'amount',)
        read_only_fields = ('id', 'ingredientGroups', 'store', 'category', 'name',)
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
    '''
    Used after placing an order for confirmation.
    '''

    food = OrderedFoodSerializer(many=True, write_only=True)
    store = ShortStoreSerializer(read_only=True)
    storeId = serializers.IntegerField(write_only=True)

    def costCheck(self, order, orderedFood, amount, cost):
        if orderedFood.cost * amount != cost:
            order.delete()
            raise CostCheckFailed()

    def create(self, validated_data):
        pickupTime = validated_data['pickupTime']
        food = validated_data['food']
        storeId = validated_data['storeId']

        if len(food) == 0:
            raise BadRequest()

        if pickupTime < timezone.now():
            raise PastOrderDenied()

        print storeId
        try:
            store = Store.objects.get(id=storeId)
        except ObjectDoesNotExist:
            raise DoesNotExist('Store does not exist')

        if pickupTime - timezone.now() < timedelta(minutes=store.minTime):
            raise MinTimeExceeded()

        pickupDay = pickupTime.weekday()
        openingHours = OpeningHours.objects.filter(store=store, day=pickupDay)
        pTime = pickupTime.time()

        for o in openingHours:
            if o.opening <= pTime <= o.closing:
                break
        else:
            # If the for loop is not stopped by the break, it means that the time of pickup is never when the store is open.
            raise StoreClosed()

        user = self.context['user']

        order = Order(user=user, store=store, pickupTime=pickupTime)
        order.save()
        for f in food:
            orderedFood = OrderedFood()
            amount = f['amount'] if 'amount' in f else 1

            if 'referenceId' in f:
                referenceFood = Food.objects.filter(id=f['referenceId'])
                if len(referenceFood) == 0:
                    raise DoesNotExist('Referenced food does not exist.')
                orderedFood = OrderedFood(**referenceFood.values()[0])

                self.costCheck(order, orderedFood, amount, f['cost'])

                orderedFood.pk = None
                orderedFood.order = order
            else:
                orderedFood.store = store

                ingredientIds = [ingredient.id for ingredient in f['ingredients']]
                exact, closestFood = OrderedFood.objects.closestFood(orderedFood, ingredientIds)
                orderedFood.cost = closestFood.cost if exact else OrderedFood.calculateCost(Ingredient.objects.filter(id__in=ingredientIds, store_id=store), closestFood)

                self.costCheck(order, orderedFood, amount, f['cost'])

                orderedFood.name = closestFood.name
                orderedFood.foodType = closestFood.foodType
                orderedFood.order = order

                orderedFood.save()
                orderedFood.ingredients = f['ingredients']

            orderedFood.amount = amount
            orderedFood.save()

        order.save()
        return order

    class Meta:
        model = Order
        fields = ('id', 'store', 'storeId', 'pickupTime', 'paid', 'total', 'food',)
        read_only_fields = ('id', 'paid', 'total', 'store',)
        write_only_fields = ('storeId', 'pickupTime', 'food',)


class OrderSerializer(serializers.ModelSerializer):
    '''
    Used for listing a specific or all orders.
    '''

    store = StoreSerializer(read_only=True)
    food = OrderedFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'food',)
        read_only_fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'food',)


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
