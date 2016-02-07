# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from math import ceil

from django.db import migrations, models


def minTimeForward(apps, schema_editor):
    Store = apps.get_model('lunch', 'Store')
    for store in Store.objects.all():
        store.minTime = store.minTime * 60000000
        store.save()


def minTimeReverse(apps, schema_editor):
    Store = apps.get_model('lunch', 'Store')
    for store in Store.objects.all():
        store.minTime = datetime.timedelta(
            minutes=ceil(
                store.minTime.total_seconds() / 60000000
            )
        )
        store.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0033_store_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='minTime',
            field=models.DurationField(default=datetime.timedelta(0, 60)),
        ),
        migrations.RunPython(minTimeForward, minTimeReverse),
    ]
