# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0029_food_desc_ingr_alwaysVisible'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='priority',
            field=models.BigIntegerField(default=0),
        ),
    ]
