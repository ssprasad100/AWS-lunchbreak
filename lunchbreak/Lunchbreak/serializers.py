from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import fields, serializers
from versioning_prime import VersionedMixin


class PrimaryModelSerializer(serializers.ModelSerializer):

    """Enables writing via the primary key and reading with ModelSerializer."""

    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid pk "{pk_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.'),
    }

    def __init__(self, *args, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        self.queryset = kwargs.pop('queryset', None)
        super(PrimaryModelSerializer, self).__init__(*args, **kwargs)

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


class RoundingDecimalField(fields.DecimalField):

    def validate_precision(self, value):
        return super().validate_precision(
            self.quantize(value)
        )


class MoneyField(VersionedMixin, serializers.IntegerField):
    description = _('Valuta onafhankelijke centen')


class CostField(VersionedMixin, serializers.IntegerField):
    description = _('Valuta onafhankelijke centen dat negatief kan zijn')


class QuantityField(VersionedMixin, serializers.IntegerField):
    description = _('Gewichten en hoeveelheden')
