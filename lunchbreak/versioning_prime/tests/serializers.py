from rest_framework import serializers


class TestSerializer(serializers.Serializer):
    specific_field = serializers.IntegerField()


class TestField(serializers.Field):
    pass
