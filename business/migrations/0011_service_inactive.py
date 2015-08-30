# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0010_token_registration_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeetoken',
            name='active',
        ),
        migrations.RemoveField(
            model_name='stafftoken',
            name='active',
        ),
        migrations.AlterField(
            model_name='employeetoken',
            name='service',
            field=models.IntegerField(default=2, verbose_name='Notification service', choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')]),
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='service',
            field=models.IntegerField(default=2, verbose_name='Notification service', choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')]),
        ),
    ]
