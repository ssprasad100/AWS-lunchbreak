# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0013_food_type_notnull'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultingredientgroup',
            name='cost',
            field=models.DecimalField(default=-1, max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='cost',
            field=models.DecimalField(default=-1, max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
    ]
