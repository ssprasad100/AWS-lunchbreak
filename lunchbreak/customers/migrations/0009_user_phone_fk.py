# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0008_user_phone_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='confirmed_at',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='phone_link',
            new_name='phone'
        ),
    ]
