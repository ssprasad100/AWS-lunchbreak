# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0028_food_cancomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='alwaysVisible',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='food',
            name='description',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
    ]
