# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def foodIngredientsForward(apps, schema_editor):
    Food = apps.get_model('lunch', 'Food')
    for food in Food.objects.select_related('foodType').all():
        for ingredient in food.ingredients.all():
            ingredient.selected = True
            ingredient.save()
        food.ingredientGroups = food.foodType.ingredientgroup_set.filter(
            store_id=food.store_id
        )
        food.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0036_ingredientgroup_costcalculation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='alwaysVisible',
        ),
        migrations.AddField(
            model_name='food',
            name='ingredientGroups',
            field=models.ManyToManyField(to='lunch.IngredientGroup', blank=True),
        ),
        migrations.AddField(
            model_name='foodtype',
            name='customisable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ingredientrelation',
            name='selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='holidayperiod',
            name='description',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.RunPython(foodIngredientsForward),
    ]
