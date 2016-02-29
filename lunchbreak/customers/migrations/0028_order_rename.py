# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0027_reservation_rename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='pickupTime',
            new_name='pickup',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='orderedTime',
            new_name='placed',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='confirmedTotal',
            new_name='total_confirmed',
        ),
    ]
