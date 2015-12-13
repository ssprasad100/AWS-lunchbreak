# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0006_refund'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refund',
            old_name='created_At',
            new_name='created_at',
        ),
    ]
