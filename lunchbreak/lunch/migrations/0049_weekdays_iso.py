# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0048_period_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryperiod',
            name='opening_day',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag'), (7, b'Zondag')]),
        ),
        migrations.AlterField(
            model_name='openingperiod',
            name='opening_day',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag'), (7, b'Zondag')]),
        ),
    ]
