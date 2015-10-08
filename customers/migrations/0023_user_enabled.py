# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0022_order_confirmedtotal_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
