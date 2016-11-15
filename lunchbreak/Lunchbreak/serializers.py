from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class PrimaryModelSerializer(serializers.ModelSerializer):

    """Enables writing via the primary key and reading with ModelSerializer."""

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        self.queryset = kwargs.pop('queryset', None)
        super(PrimaryModelSerializer, self).__init__(**kwargs)

    def get_queryset(self):
        return self.queryset

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class RequestAttributeDefault():

    def __init__(self, attribute, raise_exception=True, fallback=None):
        if not isinstance(attribute, str):
            raise ValueError('Given attribute needs to be a string.')

        self.attribute = attribute
        self.raise_exception = raise_exception
        self.fallback = fallback

    def set_context(self, serializer_field):
        try:
            attributes = self.attribute.split('.')
            self.value = serializer_field.context['request']
            for attribute in attributes:
                self.value = getattr(self.value, attribute)
        except AttributeError:
            if self.raise_exception:
                raise
            self.value = self.fallback

    def __call__(self):
        return self.value

    def __repr__(self):
        return '{class_name}({attribute}, {raise_exception}, {fallback})'.format(
            class_name=self.__class__.__name__,
            attribute=self.attribute,
            raise_exception=self.raise_exception,
            fallback=self.fallback
        )
