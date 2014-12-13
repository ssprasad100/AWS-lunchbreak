# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0007_verbose_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultfood',
            name='ingredients',
            field=models.ManyToManyField(to=b'lunch.DefaultIngredient', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='ingredients',
            field=models.ManyToManyField(to=b'lunch.Ingredient', null=True, blank=True),
        ),
    ]
