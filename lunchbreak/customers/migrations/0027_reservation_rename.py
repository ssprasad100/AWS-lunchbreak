# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0026_user_rename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='placedTime',
            new_name='placed',
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name='reservationTime',
            new_name='reservation_time',
        ),
    ]
