# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from lunch.config import COST_GROUP_BOTH


def costGroupForward(apps, schema_editor):
    IngredientGroup = apps.get_model('lunch', 'IngredientGroup')
    for ingredientGroup in IngredientGroup.objects.all():
        if ingredientGroup.cost < 0:
            ingredientGroup.cost = 0
            ingredientGroup.costCalculation = COST_GROUP_BOTH
            ingredientGroup.save()


def costGroupReverse(apps, schema_editor):
    IngredientGroup = apps.get_model('lunch', 'IngredientGroup')
    for ingredientGroup in IngredientGroup.objects.all():
        if ingredientGroup.costCalculation == COST_GROUP_BOTH:
            ingredientGroup.cost = -1
            ingredientGroup.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0035_store_maxseats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='costCalculation',
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='costCalculation',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Altijd de groepsprijs'), (1, b'Duurder bij toevoegen, zelfde bij aftrekken'), (2, b'Duurder bij toevoegen, goedkoper bij aftrekken')]),
        ),
        migrations.AlterField(
            model_name='ingredientgroup',
            name='cost',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.RunPython(costGroupForward, costGroupReverse),
    ]
