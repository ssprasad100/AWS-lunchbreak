# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0008_auto_20151214_0327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payout',
            name='amount',
            field=models.DecimalField(null=True, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='payout',
            name='currency',
            field=models.CharField(blank=True, max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')]),
        ),
        migrations.AlterField(
            model_name='payout',
            name='status',
            field=models.CharField(default=b'pending', max_length=255, choices=[(b'pending', b'Pending'), (b'paid', b'Paid')]),
        ),
    ]
