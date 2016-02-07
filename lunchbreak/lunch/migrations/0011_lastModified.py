# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0010_defaultingredientgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultfood',
            name='lastModified',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 22, 19, 52, 28, 181028), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='defaultingredient',
            name='lastModified',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 22, 19, 52, 37, 627124), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='food',
            name='lastModified',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 22, 19, 52, 48, 717713), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='lastModified',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 22, 19, 52, 49, 996223), auto_now=True),
            preserve_default=False,
        ),
    ]
