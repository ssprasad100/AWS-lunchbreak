# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0006_ordfood_original'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderedfood',
            name='useOriginal',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='cost',
            field=models.DecimalField(max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
    ]
