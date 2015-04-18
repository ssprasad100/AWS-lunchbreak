# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0008_ingrelation_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodtype',
            name='required',
            field=models.ManyToManyField(to='lunch.IngredientGroup'),
            preserve_default=True,
        ),
    ]
