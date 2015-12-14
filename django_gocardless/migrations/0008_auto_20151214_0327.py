# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0007_auto_20151213_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='swedish_identifity_number',
            new_name='swedish_identity_number',
        ),
    ]
