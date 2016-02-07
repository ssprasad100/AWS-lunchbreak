# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0031_storeheader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='header',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='lunch.StoreHeader', null=True),
        ),
    ]
