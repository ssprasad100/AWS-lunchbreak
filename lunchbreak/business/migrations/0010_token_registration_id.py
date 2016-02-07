# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0009_token_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetoken',
            name='registration_id',
            field=models.TextField(verbose_name='Registration ID', blank=True),
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='registration_id',
            field=models.TextField(verbose_name='Registration ID', blank=True),
        ),
    ]
