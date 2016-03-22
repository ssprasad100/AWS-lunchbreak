# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0001_initial'),
        ('business', '0016_staff_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='merchant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='django_gocardless.Merchant', null=True),
        ),
    ]
