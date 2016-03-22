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
            field=models.CharField(default='First name', help_text='First name', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staff',
            name='last_name',
            field=models.CharField(default='Last name', help_text='Last name', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='staff',
            name='email',
            field=models.EmailField(help_text='Email address', unique=True, max_length=255),
        ),
    ]
