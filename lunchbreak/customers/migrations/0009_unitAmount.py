# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0008_heart'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderedfood',
            name='unitAmount',
            field=models.DecimalField(null=True, max_digits=7, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='amount',
            field=models.PositiveIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='cost',
            field=models.DecimalField(max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='device',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
