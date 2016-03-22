# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchant',
            name='access_token',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='organisation_id',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='state',
            field=models.CharField(help_text='CSRF Token', max_length=56, blank=True),
        ),
    ]
