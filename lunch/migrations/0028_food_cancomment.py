# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0027_minDays'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='canComment',
            field=models.BooleanField(default=False),
        ),
    ]
