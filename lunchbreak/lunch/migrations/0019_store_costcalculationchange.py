# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0018_store_costcalculation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='costCalculation',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Altijd de groepsprijs'), (1, b'Duurder bij toevoegen, zelfde bij aftrekken')]),
            preserve_default=True,
        ),
    ]
