# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0013_orderedfood_foodamount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='confirmedTotal',
            field=models.DecimalField(default=None, null=True, max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
    ]
