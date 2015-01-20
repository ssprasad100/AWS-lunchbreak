# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0005_foodcat_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='number',
            field=models.PositiveIntegerField(),
        ),
    ]
