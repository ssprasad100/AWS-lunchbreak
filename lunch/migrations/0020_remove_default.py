# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0019_store_costcalculationchange'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defaultfood',
            name='category',
        ),
        migrations.RemoveField(
            model_name='defaultfood',
            name='foodType',
        ),
        migrations.RemoveField(
            model_name='defaultfood',
            name='ingredients',
        ),
        migrations.DeleteModel(
            name='DefaultFoodCategory',
        ),
        migrations.RemoveField(
            model_name='defaultingredient',
            name='group',
        ),
        migrations.RemoveField(
            model_name='defaultingredientgroup',
            name='foodType',
        ),
        migrations.DeleteModel(
            name='DefaultIngredientGroup',
        ),
        migrations.AlterUniqueTogether(
            name='defaultingredientrelation',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='defaultingredientrelation',
            name='food',
        ),
        migrations.DeleteModel(
            name='DefaultFood',
        ),
        migrations.RemoveField(
            model_name='defaultingredientrelation',
            name='ingredient',
        ),
        migrations.DeleteModel(
            name='DefaultIngredient',
        ),
        migrations.DeleteModel(
            name='DefaultIngredientRelation',
        ),
    ]
