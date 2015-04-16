# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0005_storecat_icons'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defaultfood',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='food',
            name='ingredients',
        ),
    ]
