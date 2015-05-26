# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0015_hearts_foodingr_notnull'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodtype',
            name='required',
        ),
        migrations.AddField(
            model_name='defaultingredientgroup',
            name='foodType',
            field=models.ForeignKey(default=2, to='lunch.FoodType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='defaultingredientgroup',
            name='minimum',
            field=models.PositiveIntegerField(default=0, verbose_name=b'Minimum amount'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='foodType',
            field=models.ForeignKey(default=2, to='lunch.FoodType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='minimum',
            field=models.PositiveIntegerField(default=0, verbose_name=b'Minimum amount'),
            preserve_default=True,
        ),
    ]
