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
