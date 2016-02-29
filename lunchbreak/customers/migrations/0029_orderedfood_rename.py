# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0028_order_rename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderedfood',
            old_name='useOriginal',
            new_name='is_original',
        ),
        migrations.RemoveField(
            model_name='orderedfood',
            name='foodAmount',
        ),
    ]
