# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields
import lunch.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultFood',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('cost', models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultFoodCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'Default food categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('cost', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('cost', models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'Food categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('iconId', models.IntegerField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=64, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('cost', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('maximum', models.IntegerField(default=0, verbose_name=b'Maximum amount')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orderedTime', models.DateTimeField(auto_now_add=True, verbose_name=b'Time of order')),
                ('pickupTime', models.DateTimeField(verbose_name=b'Time of pickup')),
                ('status', models.IntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Accepted'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed')])),
                ('paid', models.BooleanField(default=False)),
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
                ('icon', models.ForeignKey(blank=True, to='lunch.Icon', null=True)),
                ('ingredients', models.ManyToManyField(to='lunch.Ingredient', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('country', models.CharField(max_length=256)),
                ('province', models.CharField(max_length=256)),
                ('city', models.CharField(max_length=256)),
                ('code', models.CharField(max_length=20, verbose_name=b'Postal code')),
                ('street', models.CharField(max_length=256)),
                ('number', models.IntegerField()),
                ('latitude', models.DecimalField(max_digits=10, decimal_places=7, blank=True)),
                ('longitude', models.DecimalField(max_digits=10, decimal_places=7, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoreCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name_plural': 'Store categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=lunch.models.tokenGenerator, max_length=64)),
                ('device', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(unique=True, max_length=128)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('digitsId', models.CharField(max_length=10, unique=True, null=True, verbose_name=b'Digits ID', blank=True)),
                ('requestId', models.CharField(max_length=32, null=True, verbose_name=b'Digits Request ID', blank=True)),
                ('confirmedAt', models.DateField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.ForeignKey(to='lunch.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='categories',
            field=models.ManyToManyField(to='lunch.StoreCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='food',
            field=models.ManyToManyField(to='lunch.OrderedFood'),
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
            field=models.ForeignKey(to='lunch.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='group',
            field=models.ForeignKey(to='lunch.IngredientGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='icon',
            field=models.ForeignKey(to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='category',
            field=models.ForeignKey(blank=True, to='lunch.FoodCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='icon',
            field=models.ForeignKey(blank=True, to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultingredient',
            name='group',
            field=models.ForeignKey(to='lunch.IngredientGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultingredient',
            name='icon',
            field=models.ForeignKey(to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='category',
            field=models.ForeignKey(blank=True, to='lunch.DefaultFoodCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='icon',
            field=models.ForeignKey(blank=True, to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.DefaultIngredient', null=True, blank=True),
            preserve_default=True,
        ),
    ]
