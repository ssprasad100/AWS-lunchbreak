# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0007_baredevice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetoken',
            name='active',
            field=models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active'),
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='active',
            field=models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active'),
        ),
    ]
