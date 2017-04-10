from rest_framework import serializers


class MerchantSerializer(serializers.ModelSerializer):

    class Meta:
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
