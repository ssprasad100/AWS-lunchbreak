# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0037_new_ingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodtype',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='icon',
        ),
    ]
