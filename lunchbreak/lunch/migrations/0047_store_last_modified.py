# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0046_store_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='food',
            old_name='modified',
            new_name='last_modified',
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='modified',
            new_name='last_modified',
        ),
        migrations.RenameField(
            model_name='quantity',
            old_name='modified',
            new_name='last_modified',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='modified',
            new_name='last_modified',
        ),
    ]
