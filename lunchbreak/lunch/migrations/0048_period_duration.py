# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0047_store_last_modified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryperiod',
            name='closing_day',
        ),
        migrations.RemoveField(
            model_name='deliveryperiod',
            name='closing_time',
        ),
        migrations.RemoveField(
            model_name='openingperiod',
            name='closing_day',
        ),
        migrations.RemoveField(
            model_name='openingperiod',
            name='closing_time',
        ),
        migrations.AddField(
            model_name='deliveryperiod',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(0, 28800)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='openingperiod',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(0, 28800)),
            preserve_default=False,
        ),
    ]
