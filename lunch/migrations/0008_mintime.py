# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0007_holidayperiod_openinghours'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='minTime',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingredientgroup',
            name='maximum',
            field=models.PositiveIntegerField(default=0, verbose_name=b'Maximum amount'),
        ),
    ]
