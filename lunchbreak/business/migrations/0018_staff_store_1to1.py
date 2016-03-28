# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0017_staff_merchant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='store',
            field=models.OneToOneField(null=True, to='lunch.Store'),
        ),
    ]
