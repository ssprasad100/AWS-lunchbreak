# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0003_ingrgroup_prior'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodtype',
            name='quantifier',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
    ]
