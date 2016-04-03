# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0041_rename'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='foodcategory',
            unique_together=set([('name', 'store')]),
        ),
    ]
