# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0012_identifier_hashed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='email',
            field=models.EmailField(unique=True, max_length=255),
        ),
    ]
