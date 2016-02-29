# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0025_reservation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='confirmedAt',
            new_name='confirmed_at',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='digitsId',
            new_name='digits_id',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='requestId',
            new_name='request_id',
        ),
    ]
