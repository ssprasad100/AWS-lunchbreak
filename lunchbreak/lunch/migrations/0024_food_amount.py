# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0023_store_lastmodified'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='amount',
            field=models.DecimalField(default=1, max_digits=7, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='inputType',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Aantal'), (1, b'Aanpasbaar o.b.v. SI-eenheid'), (2, b'Vaste hoeveelheid o.b.v. SI-eenheid')]),
            preserve_default=True,
        ),
    ]
