# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0049_weekdays_iso'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deliveryperiod',
            old_name='opening_day',
            new_name='day',
        ),
        migrations.RenameField(
            model_name='deliveryperiod',
            old_name='opening_time',
            new_name='time',
        ),
        migrations.RenameField(
            model_name='openingperiod',
            old_name='opening_day',
            new_name='day',
        ),
        migrations.RenameField(
            model_name='openingperiod',
            old_name='opening_time',
            new_name='time',
        ),
    ]
