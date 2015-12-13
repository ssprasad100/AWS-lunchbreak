# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0004_auto_20151213_0356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default=b'pending_submission', max_length=255, choices=[(b'pending_submission', b'Pending submission'), (b'submitted', b'Submitted'), (b'confirmed', b'Confirmed'), (b'failed', b'Failed'), (b'charged_back', b'Charged back'), (b'paid_out', b'Paid out'), (b'cancelled', b'Cancelled'), (b'pending_customer_approval', b'Pending customer approval'), (b'customer_approval_denied', b'Customer approval denied')]),
        ),
    ]
