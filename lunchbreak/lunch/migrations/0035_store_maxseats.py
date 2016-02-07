# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0034_store_mintime_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='maxSeats',
            field=models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
