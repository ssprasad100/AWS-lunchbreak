# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0038_remove_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='number',
            field=models.CharField(max_length=10),
        ),
    ]
