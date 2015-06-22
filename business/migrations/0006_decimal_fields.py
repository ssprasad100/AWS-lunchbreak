# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_passwordmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employeetoken',
            name='device',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='email',
            field=models.EmailField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='password',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='device',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
