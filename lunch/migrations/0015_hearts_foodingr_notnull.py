# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0008_heart'),
        ('lunch', '0014_ingredientgroup_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='hearts',
            field=models.ManyToManyField(to='customers.User', through='customers.Heart', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultfood',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.DefaultIngredient', through='lunch.DefaultIngredientRelation', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='food',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient', through='lunch.IngredientRelation', blank=True),
            preserve_default=True,
        ),
    ]
