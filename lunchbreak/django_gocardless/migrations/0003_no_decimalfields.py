# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-31 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0002_rf_completion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount_refunded',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='payout',
            name='amount',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='refund',
            name='amount',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
    ]
