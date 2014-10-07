from ordering.models import Store

from rest_framework import serializers


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = ('id', 'name', 'country', 'province', 'code', 'street', 'number', 'lat', 'lon')