from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
from pendulum import Pendulum
from rest_framework import serializers


class RoundingDecimalField(models.DecimalField):

    def __init__(self, *args, rounding, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounding = None
    def to_python(self, value):
        value = super().to_python(value)

        if value is None:
            return value

        exponent = Decimal('1.' + ('0' * self.decimal_places))
        return value.quantize(exponent, rounding=self.rounding)


class DefaultTimeZoneDateTimeField(serializers.DateTimeField):

    def to_representation(self, value):
        value = Pendulum.instance(
            value
        ).in_timezone(
            settings.TIME_ZONE
        )._datetime
        return super().to_representation(value)


class StatusSignalMixin:

    def __init__(self, choices, *args, **kwargs):
        # Check if choices contain signals.
        # Because this function is also called in migrations.
        if choices and len(choices[0]) > 2:
            self.signals = {value: signal for value, display, signal in choices}
            choices = ((value, display,) for value, display, signal in choices)
        super().__init__(*args, choices=choices, **kwargs)

    def contribute_to_class(self, cls, *args, **kwargs):
        """Add get_{field}_signal methods to class."""
        # Cannot load models when the app hasn't loaded yet.
        # When importing here, it's definitely loaded.
        from .models import StatusSignalModel

        super().contribute_to_class(cls, *args, **kwargs)
        if issubclass(cls, StatusSignalModel):
            setattr(
                cls,
                'get_{name}_signal'.format(
                    name=self.name
                ),
                curry(
                    cls._get_FIELD_signal,
                    field=self
                )
            )


class StatusSignalField(StatusSignalMixin, models.PositiveIntegerField):
    pass


class MoneyField(models.PositiveIntegerField):
    description = _('Valuta onafhankelijke centen')


class CostField(models.IntegerField):
    description = _('Valuta onafhankelijke centen dat negatief kan zijn')
