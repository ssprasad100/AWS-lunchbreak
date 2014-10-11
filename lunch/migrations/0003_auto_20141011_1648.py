# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0002_auto_20141008_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterField(
            model_name='store',
            name='latitude',
            field=models.DecimalField(max_digits=10, decimal_places=7, blank=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='longitude',
            field=models.DecimalField(max_digits=10, decimal_places=7, blank=True),
        ),
    ]
