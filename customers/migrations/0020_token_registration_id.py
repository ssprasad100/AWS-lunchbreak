# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0019_orderedfood_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='registration_id',
            field=models.TextField(verbose_name='Registration ID', blank=True),
        ),
    ]
