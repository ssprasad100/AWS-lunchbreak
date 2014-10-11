# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0004_auto_20141011_2047'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientgroup',
            old_name='groupName',
            new_name='name',
        ),
    ]
