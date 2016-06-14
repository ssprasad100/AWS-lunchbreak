# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_gocardless.mixins


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('address_line1', models.CharField(max_length=255, blank=True)),
                ('address_line2', models.CharField(max_length=255, blank=True)),
                ('address_line3', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('company_name', models.CharField(help_text='Required unless family_name and given_name are provided.', max_length=255, blank=True)),
                ('country_code', models.CharField(max_length=2, blank=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('family_name', models.CharField(max_length=255, blank=True)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('language', models.CharField(max_length=2, blank=True)),
                ('postal_code', models.CharField(max_length=255, blank=True)),
                ('region', models.CharField(max_length=255, blank=True)),
                ('swedish_identity_number', models.CharField(max_length=255, blank=True)),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCacheMixin),
        ),
        migrations.CreateModel(
            name='CustomerBankAccount',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('account_holder_name', models.CharField(max_length=18)),
                ('account_number_ending', models.CharField(max_length=2)),
                ('bank_name', models.CharField(max_length=255)),
                ('country_code', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(null=True)),
                ('currency', models.CharField(max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('enabled', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(blank=True, to='django_gocardless.Customer', null=True)),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCacheMixin),
        ),
        migrations.CreateModel(
            name='Mandate',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True, blank=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('next_possible_charge_date', models.DateField(null=True)),
                ('reference', models.CharField(max_length=255, blank=True)),
                ('scheme', models.CharField(blank=True, max_length=255, choices=[(b'autogiro', b'Autogiro'), (b'bacs', b'Bacs'), (b'sepa_core', b'Sepa Core'), (b'sepa_cor1', b'Sepa Cor1')])),
                ('status', models.CharField(default=b'pending_submission', max_length=255, choices=[(b'pending_submission', b'Pending submission'), (b'submitted', b'Submitted'), (b'active', b'Active'), (b'failed', b'Failed'), (b'cancelled', b'Cancelled'), (b'expired', b'Expired')])),
                ('customer_bank_account', models.OneToOneField(null=True, blank=True, to='django_gocardless.CustomerBankAccount')),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCacheMixin),
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=255, blank=True)),
                ('organisation_id', models.CharField(max_length=255, blank=True)),
                ('state', models.CharField(help_text='CSRF Token', max_length=56, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('amount_refunded', models.DecimalField(max_digits=12, decimal_places=2)),
                ('charge_date', models.DateField(null=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('currency', models.CharField(max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('description', models.TextField(blank=True)),
                ('reference', models.CharField(max_length=140, blank=True)),
                ('status', models.CharField(default=b'pending_submission', max_length=255, choices=[(b'pending_submission', b'Pending submission'), (b'submitted', b'Submitted'), (b'confirmed', b'Confirmed'), (b'failed', b'Failed'), (b'charged_back', b'Charged back'), (b'paid_out', b'Paid out'), (b'cancelled', b'Cancelled'), (b'pending_customer_approval', b'Pending customer approval'), (b'customer_approval_denied', b'Customer approval denied')])),
                ('mandate', models.ForeignKey(to='django_gocardless.Mandate', null=True)),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCreateMixin),
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(null=True, max_digits=12, decimal_places=2)),
                ('created_at', models.DateTimeField(null=True)),
                ('currency', models.CharField(blank=True, max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('reference', models.CharField(max_length=140, blank=True)),
                ('status', models.CharField(default=b'pending', max_length=255, choices=[(b'pending', b'Pending'), (b'paid', b'Paid')])),
                ('merchant', models.ForeignKey(to='django_gocardless.Merchant', null=True)),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCacheMixin),
        ),
        migrations.CreateModel(
            name='RedirectFlow',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('description', models.TextField(blank=True)),
                ('scheme', models.CharField(blank=True, max_length=255, null=True, choices=[(b'autogiro', b'Autogiro'), (b'bacs', b'Bacs'), (b'sepa_core', b'Sepa Core'), (b'sepa_cor1', b'Sepa Cor1')])),
                ('session_token', models.CharField(max_length=255, blank=True)),
                ('redirect_url', models.URLField(blank=True)),
                ('customer', models.OneToOneField(null=True, blank=True, to='django_gocardless.Customer')),
                ('customer_bank_account', models.OneToOneField(null=True, blank=True, to='django_gocardless.CustomerBankAccount')),
                ('mandate', models.OneToOneField(null=True, blank=True, to='django_gocardless.Mandate')),
                ('merchant', models.ForeignKey(blank=True, to='django_gocardless.Merchant', null=True)),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCreateMixin),
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(null=True, max_digits=12, decimal_places=2)),
                ('created_at', models.DateTimeField(null=True)),
                ('currency', models.CharField(blank=True, max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('reference', models.CharField(max_length=140, blank=True)),
                ('payment', models.ForeignKey(to='django_gocardless.Payment', null=True)),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCacheMixin),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('count', models.PositiveIntegerField(null=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('currency', models.CharField(max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('day_of_month', models.IntegerField(null=True, choices=[(-1, b'-1'), (1, b'1'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5'), (6, b'6'), (7, b'7'), (8, b'8'), (9, b'9'), (10, b'10'), (11, b'11'), (12, b'12'), (13, b'13'), (14, b'14'), (15, b'15'), (16, b'16'), (17, b'17'), (18, b'18'), (19, b'19'), (20, b'20'), (21, b'21'), (22, b'22'), (23, b'23'), (24, b'24'), (25, b'25'), (26, b'26'), (27, b'27'), (28, b'28')])),
                ('end_date', models.DateField(null=True)),
                ('interval', models.PositiveIntegerField(default=1)),
                ('interval_unit', models.CharField(max_length=255, choices=[(b'weekly', b'Weekly'), (b'monthly', b'Monthly'), (b'yearly', b'Yearly')])),
                ('month', models.CharField(blank=True, max_length=255, choices=[(b'january', b'January'), (b'february', b'February'), (b'march', b'March'), (b'april', b'April'), (b'may', b'May'), (b'june', b'June'), (b'july', b'July'), (b'august', b'August'), (b'september', b'September'), (b'october', b'October'), (b'november', b'November'), (b'december', b'December')])),
                ('name', models.CharField(max_length=255, blank=True)),
                ('payment_reference', models.CharField(max_length=140, blank=True)),
                ('start_date', models.DateField(null=True)),
                ('status', models.CharField(default=b'pending_customer_approval', max_length=255, choices=[(b'pending_customer_approval', b'Pending customer approval'), (b'customer_approval_denied', b'Customer approval denied'), (b'active', b'Active'), (b'finished', b'Finished'), (b'cancelled', b'Cancelled')])),
                ('mandate', models.ForeignKey(to='django_gocardless.Mandate')),
            ],
            bases=(models.Model, django_gocardless.mixins.GCCreateUpdateMixin),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout',
            field=models.ForeignKey(to='django_gocardless.Payout', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='subscription',
            field=models.ForeignKey(to='django_gocardless.Subscription', null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='merchant',
            field=models.ForeignKey(blank=True, to='django_gocardless.Merchant', help_text='Merchant if not a direct customer.', null=True),
        ),
    ]
