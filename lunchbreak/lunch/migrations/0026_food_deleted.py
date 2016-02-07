# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0025_food_minDays'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='minDays',
        ),
        migrations.RemoveField(
            model_name='store',
            name='minDaysTime',
        ),
        migrations.AddField(
            model_name='food',
            name='deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
