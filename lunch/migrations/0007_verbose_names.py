# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0006_orders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientgroup',
            name='maximum',
            field=models.IntegerField(default=0, verbose_name=b'Maximum amount'),
        ),
        migrations.AlterField(
            model_name='order',
            name='orderedTime',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Time of order'),
        ),
        migrations.AlterField(
            model_name='order',
            name='pickupTime',
            field=models.DateTimeField(verbose_name=b'Time of pickup'),
        ),
        migrations.AlterField(
            model_name='user',
            name='requestId',
            field=models.CharField(max_length=32, null=True, verbose_name=b'Request ID', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='userId',
            field=models.CharField(max_length=10, null=True, verbose_name=b'User ID', blank=True),
        ),
    ]
