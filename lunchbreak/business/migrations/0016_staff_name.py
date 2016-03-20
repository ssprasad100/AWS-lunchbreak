# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0015_staff_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='first_name',
            field=models.CharField(default='First name', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staff',
            name='last_name',
            field=models.CharField(default='Last name', max_length=255),
            preserve_default=False,
        ),
    ]
