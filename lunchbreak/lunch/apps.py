from django.apps import AppConfig
from django.db import models
from Lunchbreak.fields import RoundingDecimalField as ModelRoundingDecimalField
from Lunchbreak.fields import DefaultTimeZoneDateTimeField
from Lunchbreak.serializers import \
    RoundingDecimalField as SerializerRoundingDecimalField
from rest_framework.serializers import ModelSerializer


class LunchConfig(AppConfig):
    name = 'lunch'
    verbose_name = 'Basis'

    def ready(self):
        ModelSerializer.serializer_field_mapping[
            models.DateTimeField] = DefaultTimeZoneDateTimeField
        ModelSerializer.serializer_field_mapping[
            ModelRoundingDecimalField] = SerializerRoundingDecimalField
