# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from customers.models import Store
from django.db import migrations, models


def minTimeMinutesToMicroSeconds(apps, schema_editor):
    for store in Store.objects.all():
        store.minTime = store.minTime * 60000000
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
        migrations.RunPython(minTimeMinutesToMicroSeconds),
    ]
