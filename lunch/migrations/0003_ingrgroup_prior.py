# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0002_rename_postcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientgroup',
            name='priority',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='openinghours',
            name='day',
            field=models.PositiveIntegerField(choices=[(0, b'Maandag'), (1, b'Dinsdag'), (2, b'Woensdag'), (3, b'Donderdag'), (4, b'Vrijdag'), (5, b'Zaterdag'), (6, b'Zondag')]),
        ),
    ]
