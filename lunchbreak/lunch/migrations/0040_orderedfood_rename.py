# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0039_store_street'),
    ]

    operations = [
        migrations.RenameField(
            model_name='food',
            old_name='ingredientGroups',
            new_name='ingredient_groups',
        ),
    ]
