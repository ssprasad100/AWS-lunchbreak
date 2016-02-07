# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_received_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='food',
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='order',
            field=models.ForeignKey(default=27, to='customers.Order'),
            preserve_default=False,
        ),
    ]
