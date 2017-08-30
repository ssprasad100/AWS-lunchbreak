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
        'business.serializers.StoreDetailSerializer',
    ]
    version = '2.2.2'

    def backwards_serializer(self, data, obj, request):
        data['preorder_time'] = time(hour=23, minute=59, second=59)
        return data

    def forwards_serializer(self, data, request):
        if 'preorder_time' in data:
            from .models import FoodType

            FoodType.objects.filter(
                store=request.user.staff.store
            ).update(
                preorder_time=data['preorder_time']
            )
        return data


class PreorderTransformation(Transformation):

    bases = [
        'lunch.serializers.BaseFoodSerializer',
        'business.serializers.FoodSerializer',
    ]
    version = '2.2.2'

    def backwards_serializer(self, data, obj, request):
        if data['preorder_disabled']:
            # preordering is disabled, 0 means disabled on API versions pre 2.2.2.
            data['preorder_days'] = 0
            return data

        if data['preorder_days'] is not None:
            data['preorder_days'] = data['preorder_days'] + 1
            return data

        if obj.foodtype.preorder_days is not None:
            data['preorder_days'] = data['foodtype']['preorder_days'] + 1
            return data

        # preordering is disabled, 0 means disabled on API versions pre 2.2.2.
        data['preorder_days'] = 0
        return data

    def forwards_serializer(self, data, request):
        if 'preorder_days' in data and data['preorder_days'] == 0:
            data['preorder_days'] = None
            return data

        return data
