# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0024_food_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='minDays',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='minDaysTime',
            field=models.TimeField(default=datetime.datetime(2015, 7, 12, 13, 10, 27, 754528), auto_now_add=True),
            preserve_default=False,
        ),
    ]
