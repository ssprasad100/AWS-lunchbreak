# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0001_initial'),
        ('lunch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='store',
            field=models.OneToOneField(null=True, blank=True, to='lunch.Store'),
        ),
    ]
