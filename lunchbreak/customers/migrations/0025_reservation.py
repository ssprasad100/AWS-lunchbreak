# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0035_store_maxseats'),
        ('customers', '0024_identifier_hashed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seats', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('placedTime', models.DateTimeField(auto_now_add=True, verbose_name='Time of placement')),
                ('reservationTime', models.DateTimeField(verbose_name='Time of reservation')),
                ('comment', models.TextField(verbose_name='Comment from user', blank=True)),
                ('suggestion', models.DateTimeField(null=True, blank=True)),
                ('response', models.TextField(verbose_name='Response from store', blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Accepted'), (3, b'Cancelled'), (4, b'Completed'), (5, b'No show')])),
                ('store', models.ForeignKey(to='lunch.Store')),
                ('user', models.ForeignKey(to='customers.User')),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='orderedTime',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Time of placement'),
        ),
        migrations.AddField(
            model_name='order',
            name='reservation',
            field=models.OneToOneField(null=True, blank=True, to='customers.Reservation'),
        ),
    ]
