# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0002_auto_20151211_0337'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('amount_refunded', models.DecimalField(max_digits=12, decimal_places=2)),
                ('charge_date', models.DateField(null=True)),
                ('created_At', models.DateTimeField(null=True)),
                ('currency', models.CharField(max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('description', models.TextField(blank=True)),
                ('reference', models.CharField(max_length=140, blank=True)),
                ('status', models.CharField(default=b'submitted', max_length=255, choices=[(b'submitted', b'Submitted'), (b'confirmed', b'Confirmed'), (b'failed', b'Failed'), (b'charged_back', b'Charged back'), (b'paid_out', b'Paid out'), (b'cancelled', b'Cancelled'), (b'pending_customer_approval', b'Pending customer approval'), (b'customer_approval_denied', b'Customer approval denied')])),
            ],
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('created_At', models.DateTimeField(null=True)),
                ('currency', models.CharField(max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('reference', models.CharField(max_length=140, blank=True)),
                ('status', models.CharField(blank=True, max_length=255, choices=[(b'pending', b'Pending'), (b'paid', b'Paid')])),
                ('merchant', models.ForeignKey(to='django_gocardless.Merchant', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('count', models.PositiveIntegerField(null=True)),
                ('created_At', models.DateTimeField(null=True)),
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
            ],
        ),
        migrations.AlterField(
            model_name='customer',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.CharField(max_length=255, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='customerbankaccount',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='customerbankaccount',
            name='currency',
            field=models.CharField(max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')]),
        ),
        migrations.AlterField(
            model_name='customerbankaccount',
            name='id',
            field=models.CharField(max_length=255, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='mandate',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='mandate',
            name='next_possible_charge_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='mandate',
            name='status',
            field=models.CharField(default=b'pending_submission', max_length=255, choices=[(b'pending_submission', b'Pending submission'), (b'submitted', b'Submitted'), (b'active', b'Active'), (b'failed', b'Failed'), (b'cancelled', b'Cancelled'), (b'expired', b'Expired')]),
        ),
        migrations.AlterField(
            model_name='redirectflow',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='mandate',
            field=models.ForeignKey(to='django_gocardless.Mandate'),
        ),
        migrations.AddField(
            model_name='payment',
            name='mandate',
            field=models.ForeignKey(to='django_gocardless.Mandate', null=True),
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
    ]
