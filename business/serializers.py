from business.models import Employee, Staff, StaffToken
from customers.models import Order
from customers.serializers import OrderedFoodSerializer
from lunch.serializers import StoreSerializer
from rest_framework import serializers


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'store', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class StaffTokenSerializer(serializers.ModelSerializer):

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'identifier': obj.identifier,
            'device': obj.device,
            'staff_id': obj.staff_id,
        }

    class Meta:
        model = StaffToken
        fields = ('id', 'identifier', 'device', 'staff_id',)
        read_only_fields = ('id', 'identifier', 'staff_id',)


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'name', 'pin',)
        read_only_fields = ('id',)
        write_only_fields = ('pin',)


class OrderSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    food = OrderedFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'food', 'total',)
        read_only_fields = ('id', 'user', 'store', 'orderedTime', 'pickupTime', 'paid', 'food', 'total',)
