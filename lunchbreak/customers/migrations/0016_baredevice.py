# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0015_orderedfood_ingr_null_redund'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usertoken',
            old_name='device',
            new_name='name',
        ),
        migrations.AddField(
            model_name='usertoken',
            name='active',
            field=models.BooleanField(default=False, help_text='Inactive devices will not be sent notifications', verbose_name='Is active'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertoken',
            name='registration_id',
            field=models.TextField(default='', verbose_name='Registration ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertoken',
            name='service',
            field=models.IntegerField(default=1, verbose_name='Notification service', choices=[(0, b'GCM'), (1, b'APNS')]),
            preserve_default=False,
        ),
    ]
