# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.db.models.deletion
import dirtyfields.dirtyfields
import private_media.storages
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.PositiveSmallIntegerField(choices=[(1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag'), (7, b'Zondag')])),
                ('time', models.TimeField()),
                ('duration', models.DurationField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('amount', models.DecimalField(default=1, max_digits=7, decimal_places=3)),
                ('cost', models.DecimalField(max_digits=7, decimal_places=2)),
                ('preorder_days', models.PositiveIntegerField(default=0)),
                ('commentable', models.BooleanField(default=False)),
                ('priority', models.BigIntegerField(default=0)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Food',
            },
        ),
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('priority', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Food categories',
            },
        ),
        migrations.CreateModel(
            name='FoodType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('quantifier', models.CharField(max_length=255, null=True, blank=True)),
                ('inputtype', models.PositiveIntegerField(default=0, choices=[(0, b'Aantal'), (1, b'Aanpasbaar o.b.v. SI-eenheid'), (2, b'Vaste hoeveelheid o.b.v. SI-eenheid')])),
                ('customisable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='HolidayPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('closed', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('cost', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='IngredientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('maximum', models.PositiveIntegerField(default=0, verbose_name='Maximum amount')),
                ('minimum', models.PositiveIntegerField(default=0, verbose_name='Minimum amount')),
                ('priority', models.PositiveIntegerField(default=0)),
                ('cost', models.DecimalField(default=0, max_digits=7, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('calculation', models.PositiveIntegerField(default=0, choices=[(0, b'Altijd de groepsprijs'), (1, b'Duurder bij toevoegen, zelfde bij aftrekken'), (2, b'Duurder bij toevoegen, goedkoper bij aftrekken')])),
                ('foodtype', models.ForeignKey(to='lunch.FoodType')),
            ],
        ),
        migrations.CreateModel(
            name='IngredientRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('selected', models.BooleanField(default=False)),
                ('typical', models.BooleanField(default=False)),
                ('food', models.ForeignKey(to='lunch.Food')),
                ('ingredient', models.ForeignKey(to='lunch.Ingredient')),
            ],
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='OpeningPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.PositiveSmallIntegerField(choices=[(1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag'), (7, b'Zondag')])),
                ('time', models.TimeField()),
                ('duration', models.DurationField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quantity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min', models.DecimalField(default=1, max_digits=7, decimal_places=3)),
                ('max', models.DecimalField(default=10, max_digits=7, decimal_places=3)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('foodtype', models.ForeignKey(to='lunch.FoodType')),
            ],
            options={
                'verbose_name_plural': 'Quantities',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('country', models.PositiveSmallIntegerField(choices=[(0, b'Belgium'), (1, b'The Netherlands'), (2, b'Luxemburg'), (3, b'France'), (4, b'Germany')])),
                ('postcode', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
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
                ('name', models.CharField(max_length=255)),
                ('wait', models.DurationField(default=datetime.timedelta(0, 60))),
                ('preorder_time', models.TimeField(default=datetime.time(12, 0))),
                ('seats_max', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)])),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='StoreCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('icon', models.PositiveIntegerField(default=0, choices=[(0, b'Onbekend'), (100, b'Slager'), (101, b'Bakker'), (102, b'Broodjeszaak'), (200, b'Tomaten'), (300, b'Broodje')])),
            ],
            options={
                'verbose_name_plural': 'Store categories',
            },
        ),
        migrations.CreateModel(
            name='StoreHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original', models.ImageField(storage=private_media.storages.PrivateMediaStorage(), upload_to='storeheader')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='store',
            name='categories',
            field=models.ManyToManyField(to='lunch.StoreCategory'),
        ),
        migrations.AddField(
            model_name='store',
            name='header',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lunch.StoreHeader', null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='hearts',
            field=models.ManyToManyField(to='customers.User', through='customers.Heart', blank=True),
        ),
        migrations.AddField(
            model_name='store',
            name='regions',
            field=models.ManyToManyField(help_text='Active delivery regions.', to='lunch.Region'),
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('country', 'postcode')]),
        ),
        migrations.AddField(
            model_name='quantity',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='openingperiod',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='group',
            field=models.ForeignKey(to='lunch.IngredientGroup'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='holidayperiod',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='food',
            name='category',
            field=models.ForeignKey(to='lunch.FoodCategory'),
        ),
        migrations.AddField(
            model_name='food',
            name='foodtype',
            field=models.ForeignKey(to='lunch.FoodType'),
        ),
        migrations.AddField(
            model_name='food',
            name='ingredientgroups',
            field=models.ManyToManyField(to='lunch.IngredientGroup', blank=True),
        ),
        migrations.AddField(
            model_name='food',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient', through='lunch.IngredientRelation', blank=True),
        ),
        migrations.AddField(
            model_name='food',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='deliveryperiod',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AlterUniqueTogether(
            name='quantity',
            unique_together=set([('foodtype', 'store')]),
        ),
        migrations.AlterUniqueTogether(
            name='ingredientrelation',
            unique_together=set([('food', 'ingredient')]),
        ),
        migrations.AlterUniqueTogether(
            name='foodcategory',
            unique_together=set([('name', 'store')]),
        ),
    ]
