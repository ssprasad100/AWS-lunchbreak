# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0011_lastModified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultfood',
            name='category',
            field=models.ForeignKey(to='lunch.DefaultFoodCategory'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='food',
            name='category',
            field=models.ForeignKey(to='lunch.FoodCategory'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='required',
            field=models.ManyToManyField(to='lunch.IngredientGroup', null=True, blank=True),
            preserve_default=True,
        ),
    ]
