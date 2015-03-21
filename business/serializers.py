from business.models import Employee, EmployeeToken, Staff, StaffToken
from customers.models import Order, User
from customers.serializers import OrderedFoodSerializer
from lunch.models import Food, IngredientGroup
from lunch.serializers import StoreSerializer, TokenSerializer
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
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields + ('staff',)


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'name', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + ('employee',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields + ('employee',)


class PrivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name',)


class ShortOrderSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'orderedTime', 'pickupTime', 'status', 'paid', 'total',)
        read_only_fields = ('id', 'user', 'orderedTime', 'pickupTime', 'paid', 'total',)


class OrderSerializer(ShortOrderSerializer):
    food = OrderedFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ShortOrderSerializer.Meta.fields + ('food',)
        read_only_fields = ShortOrderSerializer.Meta.read_only_fields + ('food',)


class ShortIngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'priority',)
        read_only_fields = ('id', 'name', 'maximum', 'priority',)


class ShortFoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Food
        fields = ('id', 'name', 'category', 'foodType',)
        read_only_fields = ('id', 'name', 'category', 'foodType',)
