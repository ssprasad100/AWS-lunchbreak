from rest_framework import serializers

from .testcase import VersioningPrimeTestCase


class TestSerializer(serializers.Serializer):
    specific_field = serializers.IntegerField()


class TestField(serializers.Field):
    pass


class SerializerTestCase(VersioningPrimeTestCase):
    pass
