# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0008_token_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeetoken',
            old_name='name',
            new_name='device',
        ),
        migrations.RenameField(
            model_name='stafftoken',
            old_name='name',
            new_name='device',
        ),
    ]
