# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0012_foodcat_mandatory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultfood',
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='food',
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType'),
            preserve_default=True,
        ),
    ]
