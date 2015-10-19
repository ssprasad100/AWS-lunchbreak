from business.models import (Employee, EmployeeToken, PasswordModel, Staff,
                             StaffToken)
from customers.config import RESERVATION_STATUS_EMPLOYEE
from customers.models import Order, OrderedFood, Reservation, User
from lunch import serializers as lunchSerializers
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.exceptions import InvalidStoreLinking
from lunch.models import (BaseToken, Food, Ingredient, IngredientGroup,
                          IngredientRelation, Store)
from rest_framework import serializers


class StoreSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Store
        fields = (
            'id',
            'name',
            'city',
            'street',
            'latitude',
            'longitude',
            'categories',
            'heartsCount',
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'minTime',
            'orderTime',
            'costCalculation',
            'enabled',
        )
        read_only_fields = (
            'id',
            'latitude',
            'longitude',
            'heartsCount',
            'categories',
        )


class StoreSerializerV3(StoreSerializer):

    class Meta:
        model = Store
        fields = StoreSerializer.Meta.fields
        read_only_fields = StoreSerializer.Meta.read_only_fields

    def save(self):
        if 'minTime' in self.validated_data:
            self.validated_data['minTime'] *= 60
        super(StoreSerializer, self).save()


class EmployeePasswordRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id',)
        write_only_fields = fields


class StaffPasswordRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ('email',)
        write_only_fields = fields


class PasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255,
        write_only=True
    )
    passwordReset = serializers.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        write_only=True
    )

    class Meta:
        model = PasswordModel
        fields = (
            'password',
            'passwordReset',
            'email',
        )
        write_only_fields = fields


class EmployeePasswordSerializer(PasswordSerializer):

    class Meta:
        model = Employee
        fields = PasswordSerializer.Meta.fields
        write_only_fields = PasswordSerializer.Meta.write_only_fields


class StaffPasswordSerializer(PasswordSerializer):

    class Meta:
        model = Staff
        fields = PasswordSerializer.Meta.fields
        write_only_fields = PasswordSerializer.Meta.write_only_fields


class BusinessTokenSerializer(lunchSerializers.TokenSerializer):
    password = serializers.CharField(
        max_length=255,
        write_only=True
    )

    class Meta:
        model = BaseToken
        fields = lunchSerializers.TokenSerializer.Meta.fields + (
            'password',
        )
        write_only_fields = (
            'password',
        )
        read_only_fields = (
            'id',
            'identifier',
            'active',
        )


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = (
            'id',
            'store',
        )
        read_only_fields = (
            'id',
        )


class StaffTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'staff',
        )
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields
        write_only_fields = BusinessTokenSerializer.Meta.write_only_fields


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            'id',
            'name',
            'owner',
        )
        read_only_fields = (
            'id',
        )


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'employee',
        )
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields
        write_only_fields = BusinessTokenSerializer.Meta.write_only_fields


class PrivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'original',
            'cost',
            'useOriginal',
            'comment',
        )
        read_only_fields = fields


class ShortOrderSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'orderedTime',
            'pickupTime',
            'status',
            'paid',
            'total',
            'confirmedTotal',
        )
        read_only_fields = (
            'id',
            'user',
            'orderedTime',
            'pickupTime',
            'paid',
            'total',
            'confirmedTotal',
        )


class OrderSpreadSerializer(serializers.BaseSerializer):
    amount = serializers.IntegerField(
        read_only=True
    )
    average = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    # 'sum' is a built-in function in Python, use 'sm' in code and return 'sum'
    sm = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    unit = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = (
            'amount',
            'average',
            'sm',
            'unit',
        )
        read_only_fields = fields

    def to_representation(self, obj):
        return {
            'amount': obj.amount,
            'average': obj.average,
            'sum': obj.sm,
            'unit': obj.unit
        }


class OrderSerializer(ShortOrderSerializer):
    orderedFood = OrderedFoodSerializer(
        many=True,
        read_only=True,
        source='orderedfood_set'
    )

    class Meta:
        model = Order
        fields = ShortOrderSerializer.Meta.fields + (
            'orderedFood',
            'description',
        )
        read_only_fields = (
            'id',
            'user',
            'orderedTime',
            'pickupTime',
            'paid',
            'total',
            'orderedFood',
            'description',
        )


class ShortIngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'priority',
            'cost',
            'foodType',
        )
        read_only_fields = (
            'id',
        )


class IngredientRelationSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRelation
        fields = (
            'ingredient',
            'typical',
        )
        write_only_fields = fields


class ShortFoodSerializer(serializers.ModelSerializer):
    ingredients = lunchSerializers.ShortIngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True,
        required=False,
        read_only=True
    )
    ingredientRelations = IngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True,
        required=False,
        write_only=True
    )
    orderAmount = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'description',
            'amount',
            'cost',
            'foodType',
            'minDays',
            'canComment',
            'priority',

            'category',
            'ingredients',
            # 'store',

            'ingredientRelations',
            'orderAmount',
        )
        read_only_fields = (
            'id',
            'ingredients',
            'orderAmount',
        )
        write_only_fields = (
            'ingredientRelations',
        )

    def createOrUpdate(self, validated_data, food=None):
        update = food is not None
        relations = validated_data.pop('ingredientrelation_set', None)
        if not update:
            food = Food(**validated_data)
        else:
            for key, value in validated_data.iteritems():
                setattr(food, key, value)

        if relations is not None:
            for relation in relations:
                if relation['ingredient'].store_id != food.store.id:
                    raise InvalidStoreLinking()

        food.save()

        if relations is not None:
            if update:
                IngredientRelation.objects.filter(food=food).delete()
            for relation in relations:
                IngredientRelation.objects.update_or_create(
                    food=food,
                    **relation
                )

        return food

    def create(self, validated_data):
        return self.createOrUpdate(validated_data)

    def update(self, instance, validated_data):
        return self.createOrUpdate(validated_data, instance)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'cost',
            'icon',
            'alwaysVisible',
            'group',
        )
        read_only_fields = (
            'id',
        )


class IngredientGroupSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'ingredients',
            'priority',
            'cost',
            'foodType',
        )
        read_only_fields = (
            'id',
            'ingredients',
        )


class SingleFoodSerializer(lunchSerializers.SingleFoodSerializer):

    class Meta:
        model = lunchSerializers.SingleFoodSerializer.Meta.model
        fields = lunchSerializers.SingleFoodSerializer.Meta.fields + (
            'deleted',
        )
        read_only_fields = lunchSerializers.SingleFoodSerializer.Meta.read_only_fields


class ReservationSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(
        read_only=True
    )
    status = serializers.ChoiceField(
        choices=RESERVATION_STATUS_EMPLOYEE
    )

    class Meta:
        model = Reservation
        fields = (
            'id',
            'user',
            'seats',
            'placedTime',
            'reservationTime',
            'comment',
            'suggestion',
            'response',
            'status',
        )
        read_only_fields = (
            'id',
            'user',
            'placedTime',
            'reservationTime',
            'comment',
        )
