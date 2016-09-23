from rest_framework import serializers

from .models import Merchant, RedirectFlow


class RedirectFlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = RedirectFlow
        fields = (
            'redirect_url',
        )


class MerchantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Merchant
        fields = (
            'organisation_id',
            'created_at',
        )
