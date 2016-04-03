# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0018_staff_store_1to1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='merchant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='django_gocardless.Merchant', null=True),
        ),
        migrations.AlterField(
            model_name='staff',
            name='store',
            field=models.OneToOneField(null=True, blank=True, to='lunch.Store'),
        ),
    ]
