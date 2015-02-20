from business.models import Staff, Employee
from lunch.serializers import StoreSerializer
from rest_framework import serializers


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'store', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'name', 'pin',)
        read_only_fields = ('id',)
        write_only_fields = ('pin',)
