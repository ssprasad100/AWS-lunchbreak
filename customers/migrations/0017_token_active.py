# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0016_baredevice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='active',
            field=models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active'),
        ),
    ]
