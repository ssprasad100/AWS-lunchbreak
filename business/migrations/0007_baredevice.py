# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0006_decimal_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeetoken',
            old_name='device',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='stafftoken',
            old_name='device',
            new_name='name',
        ),
        migrations.AddField(
            model_name='employeetoken',
            name='active',
            field=models.BooleanField(default=False, help_text='Inactive devices will not be sent notifications', verbose_name='Is active'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employeetoken',
            name='registration_id',
            field=models.TextField(default='', verbose_name='Registration ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employeetoken',
            name='service',
            field=models.IntegerField(default=0, verbose_name='Notification service', choices=[(0, b'GCM'), (1, b'APNS')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stafftoken',
            name='active',
            field=models.BooleanField(default=False, help_text='Inactive devices will not be sent notifications', verbose_name='Is active'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stafftoken',
            name='registration_id',
            field=models.TextField(default='', verbose_name='Registration ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stafftoken',
            name='service',
            field=models.IntegerField(default=1, verbose_name='Notification service', choices=[(0, b'GCM'), (1, b'APNS')]),
            preserve_default=False,
        ),
    ]
