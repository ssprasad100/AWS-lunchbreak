from decimal import Decimal

from django.db import models


class RoundingDecimalField(models.DecimalField):

    def __init__(self, *args, rounding=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rounding = rounding

    def to_python(self, value):
        value = super().to_python(value)

        if value is None:
            return value

        exponent = Decimal('1.' + ('0' * self.decimal_places))
        return value.quantize(exponent, rounding=self.rounding)
