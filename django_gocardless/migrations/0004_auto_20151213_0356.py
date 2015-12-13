# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0003_auto_20151213_0322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='company_name',
            field=models.CharField(help_text='Required unless family_name and given_name are provided.', max_length=255, blank=True),
        ),
    ]
