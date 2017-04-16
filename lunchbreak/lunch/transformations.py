from versioning_prime import Transformation


class OnlinePaymentsTransformation(Transformation):

    bases = [
        'lunch.serializers.StoreSerializer',
    ]
    version = '2.2.0'

    def backwards_serializer(self, data, obj, request):
        data['online_payments'] = data.pop('gocardless_enabled')
        data.pop('payconiq_enabled')
        return data
