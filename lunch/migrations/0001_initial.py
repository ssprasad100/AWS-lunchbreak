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
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('cost', models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('defaultfood_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='lunch.DefaultFood')),
            ],
            options={
            },
            bases=('lunch.defaultfood',),
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('defaultingredient_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='lunch.DefaultIngredient')),
            ],
            options={
            },
            bases=('lunch.defaultingredient',),
        ),
        migrations.CreateModel(
            name='IngredientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('maximum', models.IntegerField(default=0)),
            ],
            options={
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
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Store Categories',
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
            model_name='ingredient',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
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
            name='defaultIngredients',
            field=models.ManyToManyField(to='lunch.DefaultIngredient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='ingredientGroups',
            field=models.ManyToManyField(to='lunch.IngredientGroup'),
            preserve_default=True,
        ),
    ]
