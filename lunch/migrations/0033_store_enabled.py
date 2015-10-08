# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0032_storeheader_ondelete'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='header',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lunch.StoreHeader', null=True),
        ),
    ]
