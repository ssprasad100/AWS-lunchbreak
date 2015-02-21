# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Received'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed')]),
        ),
    ]
