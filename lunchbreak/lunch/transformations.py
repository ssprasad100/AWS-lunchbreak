from datetime import time

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


class PreorderStoreTransformation(Transformation):

    bases = [
        'lunch.serializers.StoreSerializer',
    ]
    version = '2.2.2'

    def backwards_serializer(self, data, obj, request):
        data['preorder_time'] = time(hour=0, minute=0, second=1)
        return data


class PreorderTransformation(Transformation):

    bases = [
        'lunch.serializers.BaseFoodSerializer',
    ]
    version = '2.2.2'

    def backwards_serializer(self, data, obj, request):
        if not data['preorder_disabled']:
            data['preorder_days'] = data['preorder_days'] + 1
        return data
