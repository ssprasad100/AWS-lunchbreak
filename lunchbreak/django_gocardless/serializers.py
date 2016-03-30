from rest_framework import serializers

from .models import RedirectFlow


class RedirectFlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = RedirectFlow
        fields = (
            'redirect_url',
        )
