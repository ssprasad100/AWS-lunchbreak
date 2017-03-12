from django.apps import AppConfig
from django.db import models
from Lunchbreak.fields import CostField as CostModelField
from Lunchbreak.fields import MoneyField as MoneyModelField
from Lunchbreak.fields import DefaultTimeZoneDateTimeField
from Lunchbreak.serializers import CostField as CostSerializerField
from Lunchbreak.serializers import MoneyField as MoneySerializerField
from rest_framework.serializers import ModelSerializer


class LunchConfig(AppConfig):
    name = 'lunch'
    verbose_name = 'Basis'

    def ready(self):
        ModelSerializer.serializer_field_mapping[
            models.DateTimeField] = DefaultTimeZoneDateTimeField

        ModelSerializer.serializer_field_mapping[CostModelField] = CostSerializerField
        ModelSerializer.serializer_field_mapping[MoneyModelField] = MoneySerializerField
