# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0003_auto_20141011_1648'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
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
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('maximum', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientGroupName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='Category',
            new_name='StoreCategory',
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='groupName',
            field=models.ForeignKey(to='lunch.IngredientGroupName'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='ingredientGroups',
            field=models.ManyToManyField(to='lunch.IngredientGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='storecategory',
            options={'verbose_name_plural': 'Store Categories'},
        ),
    ]
