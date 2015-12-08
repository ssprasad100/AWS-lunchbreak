# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True, blank=True)),
                ('address_line1', models.CharField(max_length=255, blank=True)),
                ('address_line2', models.CharField(max_length=255, blank=True)),
                ('address_line3', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('company_name', models.CharField(max_length=255, blank=True)),
                ('country_code', models.CharField(max_length=2, blank=True)),
                ('created_at', models.DateTimeField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('family_name', models.CharField(max_length=255, blank=True)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('language', models.CharField(max_length=2, blank=True)),
                ('postal_code', models.CharField(max_length=255, blank=True)),
                ('region', models.CharField(max_length=255, blank=True)),
                ('swedish_identifity_number', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerBankAccount',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True, blank=True)),
                ('account_holder_name', models.CharField(max_length=18)),
                ('account_number_ending', models.CharField(max_length=2)),
                ('bank_name', models.CharField(max_length=255)),
                ('country_code', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(null=True, blank=True)),
                ('currency', models.CharField(max_length=3)),
                ('enabled', models.BooleanField()),
                ('customer', models.ForeignKey(blank=True, to='django_gocardless.Customer', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mandate',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True, blank=True)),
                ('created_at', models.DateTimeField(null=True, blank=True)),
                ('next_possible_charge_date', models.DateField(null=True, blank=True)),
                ('reference', models.CharField(max_length=255, blank=True)),
                ('scheme', models.CharField(blank=True, max_length=255, choices=[('autogiro', 'Autogiro'), ('bacs', 'Bacs'), ('sepa_core', 'Sepa Core'), ('sepa_cor1', 'Sepa Cor1')])),
                ('status', models.CharField(blank=True, max_length=255, choices=[('pending_submission', 'Pending submission'), ('submitted', 'Submitted'), ('active', 'Active'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('expired', 'Expired')])),
                ('customer_bank_account', models.ForeignKey(to='django_gocardless.CustomerBankAccount', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=255)),
                ('organisation_id', models.CharField(max_length=255)),
                ('state', models.CharField(help_text='CSRF Token', max_length=56)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RedirectFlow',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(null=True, blank=True)),
                ('description', models.TextField(blank=True)),
                ('scheme', models.CharField(blank=True, max_length=255, null=True, choices=[('autogiro', 'Autogiro'), ('bacs', 'Bacs'), ('sepa_core', 'Sepa Core'), ('sepa_cor1', 'Sepa Cor1')])),
                ('session_token', models.CharField(max_length=255, blank=True)),
                ('redirect_url', models.URLField(blank=True)),
                ('customer', models.ForeignKey(blank=True, to='django_gocardless.Customer', null=True)),
                ('customer_bank_account', models.ForeignKey(blank=True, to='django_gocardless.CustomerBankAccount', null=True)),
                ('mandate', models.ForeignKey(blank=True, to='django_gocardless.Mandate', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='merchant',
            field=models.ForeignKey(blank=True, to='django_gocardless.Merchant', help_text='Merchant if not a direct customer.', null=True),
        ),
    ]
