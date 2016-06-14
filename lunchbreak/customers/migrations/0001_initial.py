# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import dirtyfields.dirtyfields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=255)),
                ('province', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('postcode', models.CharField(max_length=20, verbose_name='Postal code')),
                ('street', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=10)),
                ('latitude', models.DecimalField(max_digits=10, decimal_places=7)),
                ('longitude', models.DecimalField(max_digits=10, decimal_places=7)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('billing', models.IntegerField(default=0, choices=[(0, b'Separate'), (1, b'Leader')])),
            ],
        ),
        migrations.CreateModel(
            name='Heart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Waiting'), (1, b'Accepted'), (2, b'Ignored')])),
            ],
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('leader', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('placed', models.DateTimeField(auto_now_add=True, verbose_name='Time of placement')),
                ('pickup', models.DateTimeField(verbose_name='Time of pickup')),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Received'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed'), (6, b'Not collected')])),
                ('total', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('total_confirmed', models.DecimalField(default=None, null=True, max_digits=7, decimal_places=2, blank=True)),
                ('description', models.TextField(blank=True)),
                ('payment_method', models.IntegerField(default=0, choices=[(0, b'Cash'), (1, b'GoCardless')])),
            ],
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='OrderedFood',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=1, max_digits=7, decimal_places=3)),
                ('cost', models.DecimalField(max_digits=7, decimal_places=2)),
                ('is_original', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Ordered food',
            },
        ),
        migrations.CreateModel(
            name='PaymentLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seats', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('placed', models.DateTimeField(auto_now_add=True, verbose_name='Time of placement')),
                ('reservation_time', models.DateTimeField(verbose_name='Time of reservation')),
                ('comment', models.TextField(verbose_name='Comment from user', blank=True)),
                ('suggestion', models.DateTimeField(null=True, blank=True)),
                ('response', models.TextField(verbose_name='Response from store', blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Accepted'), (3, b'Cancelled'), (4, b'Completed'), (5, b'No show')])),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
                ('name', models.CharField(max_length=255)),
                ('digits_id', models.CharField(max_length=10, unique=True, null=True, verbose_name='Digits ID', blank=True)),
                ('request_id', models.CharField(max_length=32, null=True, verbose_name='Digits Request ID', blank=True)),
                ('confirmed_at', models.DateField(null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.IntegerField(default=2, verbose_name='Notification service', choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')])),
                ('registration_id', models.TextField(verbose_name='Registration ID', blank=True)),
                ('device', models.CharField(max_length=255)),
                ('identifier', models.CharField(max_length=255)),
                ('user', models.ForeignKey(to='customers.User')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
    ]
