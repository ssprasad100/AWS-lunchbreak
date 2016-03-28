# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0002_merchant_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='redirectflow',
            name='merchant',
            field=models.ForeignKey(blank=True, to='django_gocardless.Merchant', null=True),
        ),
        migrations.AlterField(
            model_name='mandate',
            name='customer_bank_account',
            field=models.OneToOneField(null=True, blank=True, to='django_gocardless.CustomerBankAccount'),
        ),
        migrations.AlterField(
            model_name='redirectflow',
            name='customer',
            field=models.OneToOneField(null=True, blank=True, to='django_gocardless.Customer'),
        ),
        migrations.AlterField(
            model_name='redirectflow',
            name='customer_bank_account',
            field=models.OneToOneField(null=True, blank=True, to='django_gocardless.CustomerBankAccount'),
        ),
        migrations.AlterField(
            model_name='redirectflow',
            name='mandate',
            field=models.OneToOneField(null=True, blank=True, to='django_gocardless.Mandate'),
        ),
    ]
