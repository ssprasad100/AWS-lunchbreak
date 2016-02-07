# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_mail_reset_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='pin',
        ),
        migrations.AddField(
            model_name='employee',
            name='password',
            field=models.CharField(default='password', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='passwordReset',
            field=models.CharField(default=None, max_length=64, null=True),
            preserve_default=True,
        ),
    ]
