# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
                ('priority', models.PositiveIntegerField(default=0)),
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
                ('icon', models.PositiveIntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')])),
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
                ('priority', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Food categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('icon', models.PositiveIntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')])),
                ('quantifier', models.CharField(max_length=64)),
                ('inputType', models.PositiveIntegerField(default=0, choices=[(0, b'Aantal'), (1, b'Gewicht')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HolidayPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=128)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('closed', models.BooleanField(default=True)),
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
                ('icon', models.PositiveIntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')])),
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
                ('maximum', models.PositiveIntegerField(default=0, verbose_name=b'Maximum amount')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.PositiveIntegerField(choices=[(0, b'Maandag'), (1, b'Dinsdag'), (2, b'Woensdag'), (3, b'Donderdeg'), (4, b'Vrijdag'), (5, b'Zaterdag'), (6, b'Zondag')])),
                ('opening', models.TimeField()),
                ('closing', models.TimeField()),
            ],
            options={
                'verbose_name_plural': 'Opening hours',
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
                ('number', models.PositiveIntegerField()),
                ('latitude', models.DecimalField(max_digits=10, decimal_places=7, blank=True)),
                ('longitude', models.DecimalField(max_digits=10, decimal_places=7, blank=True)),
                ('minTime', models.PositiveIntegerField(default=0)),
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
        migrations.AddField(
            model_name='store',
            name='categories',
            field=models.ManyToManyField(to='lunch.StoreCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openinghours',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
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
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='holidayperiod',
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
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType', null=True),
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
            model_name='defaultfood',
            name='category',
            field=models.ForeignKey(blank=True, to='lunch.DefaultFoodCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.DefaultIngredient', null=True, blank=True),
            preserve_default=True,
        ),
    ]
