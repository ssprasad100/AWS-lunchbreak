# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields
import lunch.models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orderedTime', models.DateTimeField(auto_now_add=True, verbose_name=b'Time of order')),
                ('pickupTime', models.DateTimeField(verbose_name=b'Time of pickup')),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Accepted'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed')])),
                ('paid', models.BooleanField(default=False)),
                ('total', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderedFood',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('cost', models.DecimalField(max_digits=5, decimal_places=2)),
                ('amount', models.IntegerField(default=1)),
                ('category', models.ForeignKey(blank=True, to='lunch.FoodCategory', null=True)),
                ('foodType', models.ForeignKey(to='lunch.FoodType', null=True)),
                ('ingredients', models.ManyToManyField(to='lunch.Ingredient', null=True, blank=True)),
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('digitsId', models.CharField(max_length=10, unique=True, null=True, verbose_name=b'Digits ID', blank=True)),
                ('requestId', models.CharField(max_length=32, null=True, verbose_name=b'Digits Request ID', blank=True)),
                ('confirmedAt', models.DateField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=lunch.models.tokenGenerator, max_length=64)),
                ('device', models.CharField(max_length=128)),
                ('user', models.ForeignKey(to='customers.User')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='food',
            field=models.ManyToManyField(to='customers.OrderedFood'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to='customers.User'),
            preserve_default=True,
        ),
    ]
