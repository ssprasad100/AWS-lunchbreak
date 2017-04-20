from rest_framework import serializers

from ..mixins import VersionedMixin


class TestSerializer(VersionedMixin, serializers.Serializer):
    specific_field = serializers.IntegerField()


class TestField(VersionedMixin, serializers.Field):
    pass
