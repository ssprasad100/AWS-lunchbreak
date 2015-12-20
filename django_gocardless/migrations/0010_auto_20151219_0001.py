# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0009_auto_20151216_0320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='created_At',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='payout',
            old_name='created_At',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='subscription',
            old_name='created_At',
            new_name='created_at',
        ),
    ]
