# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0026_food_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='minDays',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='store',
            name='orderTime',
            field=models.TimeField(default=datetime.time(12, 0)),
        ),
    ]
