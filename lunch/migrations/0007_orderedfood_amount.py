# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0006_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderedfood',
            name='amount',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
