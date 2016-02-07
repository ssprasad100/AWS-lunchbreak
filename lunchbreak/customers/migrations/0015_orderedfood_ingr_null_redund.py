# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0014_order_confirmedtotal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedfood',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient', blank=True),
        ),
    ]
