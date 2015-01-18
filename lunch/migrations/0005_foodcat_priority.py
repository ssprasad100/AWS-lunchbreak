# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0004_foodtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultfoodcategory',
            name='priority',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='priority',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
