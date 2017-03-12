from decimal import Decimal

from versioning_prime import Transformation


class MoneyTransformation(Transformation):

    bases = [
        'Lunchbreak.serializers.MoneyField',
        'Lunchbreak.serializers.CostField',
    ]
    version = '2.2.0'

    def backwards_field(self, obj, data, request):
        return Decimal(obj) / Decimal(10 ** 2)

    def forwards_field(self, obj, data, request):
        return int(Decimal(data) * Decimal(10 ** 2))
