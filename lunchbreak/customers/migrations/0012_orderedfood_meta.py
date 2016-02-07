# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0011_unitamount_removed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderedfood',
            options={'verbose_name_plural': 'Ordered food'},
        ),
    ]
