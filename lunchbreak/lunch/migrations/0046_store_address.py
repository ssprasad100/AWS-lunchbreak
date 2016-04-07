# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0045_store_delivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='latitude',
            field=models.DecimalField(max_digits=10, decimal_places=7),
        ),
        migrations.AlterField(
            model_name='store',
            name='longitude',
            field=models.DecimalField(max_digits=10, decimal_places=7),
        ),
    ]
