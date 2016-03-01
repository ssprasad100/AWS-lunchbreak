# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0013_staff_email_unique'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='passwordReset',
            new_name='password_reset',
        ),
        migrations.RenameField(
            model_name='staff',
            old_name='passwordReset',
            new_name='password_reset',
        ),
    ]
