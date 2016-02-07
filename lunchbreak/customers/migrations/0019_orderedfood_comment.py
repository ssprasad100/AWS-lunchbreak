# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0018_token_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderedfood',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
    ]
