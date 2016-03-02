# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0030_group'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='payment',
            new_name='billing',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='users',
            new_name='memberships',
        ),
    ]
