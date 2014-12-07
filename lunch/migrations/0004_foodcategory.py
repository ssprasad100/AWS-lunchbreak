# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0003_auth_simplify'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultFoodCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
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
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='category',
            field=models.ForeignKey(to='lunch.DefaultFoodCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='category',
            field=models.ForeignKey(to='lunch.FoodCategory', null=True),
            preserve_default=True,
        ),
    ]
