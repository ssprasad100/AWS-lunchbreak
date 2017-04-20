from decimal import Decimal

from versioning_prime import Transformation


class MoneyTransformation(Transformation):

    bases = [
        'Lunchbreak.serializers.MoneyField',
        'Lunchbreak.serializers.CostField',
    ]
    version = '2.3.0'

    def backwards_field(self, data, obj, request):
        result = Decimal(obj) / Decimal(10 ** 2)
        return result

    def forwards_field(self, data, request):
        result = int(Decimal(data) * Decimal(10 ** 2))
        return result
