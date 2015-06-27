# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0010_order_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedfood',
            name='unitAmount',
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='amount',
            field=models.DecimalField(default=1, max_digits=7, decimal_places=3),
            preserve_default=True,
        ),
    ]
