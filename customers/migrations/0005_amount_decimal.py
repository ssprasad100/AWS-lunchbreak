# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_relname_order_ofood'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedfood',
            name='amount',
            field=models.DecimalField(default=1, max_digits=13, decimal_places=3),
            preserve_default=True,
        ),
    ]
