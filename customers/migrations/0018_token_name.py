# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0017_token_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usertoken',
            old_name='name',
            new_name='device',
        ),
    ]
