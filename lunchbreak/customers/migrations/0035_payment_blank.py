# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0034_payments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='django_gocardless.Payment', null=True),
        ),
    ]
