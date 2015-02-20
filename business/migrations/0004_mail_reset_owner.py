# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_rename_emp2staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='owner',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staff',
            name='email',
            field=models.EmailField(default='error@error.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staff',
            name='passwordReset',
            field=models.CharField(default=None, max_length=64, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='pin',
            field=models.CharField(default=None, max_length=128, null=True),
        ),
    ]
