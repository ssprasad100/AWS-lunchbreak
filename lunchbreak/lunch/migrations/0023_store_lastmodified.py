# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0022_quantity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='food',
            options={'verbose_name_plural': 'Food'},
        ),
        migrations.AlterModelOptions(
            name='quantity',
            options={'verbose_name_plural': 'Quantities'},
        ),
        migrations.AddField(
            model_name='store',
            name='lastModified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 27, 17, 39, 53, 671617), auto_now=True),
            preserve_default=False,
        ),
    ]
