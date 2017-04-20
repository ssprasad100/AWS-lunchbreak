from rest_framework import serializers

from .models import Merchant, Transaction


class MerchantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Merchant
        fields = (
            'id',
            'remote_id',
            'access_token',
        )
        read_only_fields = (
            'id',
        )
        extra_kwargs = {
            'access_token': {
                'write_only': True,
            },
        }


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = (
            'id',
            'remote_id',
            'amount',
            'currency',
            'status',
        )
        read_only_fields = fields
