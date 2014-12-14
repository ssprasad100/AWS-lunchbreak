# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0005_icon'),
    ]

    operations = [
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
                ('category', models.ForeignKey(blank=True, to='lunch.FoodCategory', null=True)),
                ('icon', models.ForeignKey(blank=True, to='lunch.Icon', null=True)),
                ('ingredients', models.ManyToManyField(to='lunch.Ingredient', null=True, blank=True)),
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
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
        migrations.RemoveField(
            model_name='user',
            name='confirmed',
        ),
        migrations.AlterField(
            model_name='defaultfood',
            name='category',
            field=models.ForeignKey(blank=True, to='lunch.DefaultFoodCategory', null=True),
        ),
        migrations.AlterField(
            model_name='defaultfood',
            name='icon',
            field=models.ForeignKey(blank=True, to='lunch.Icon', null=True),
        ),
        migrations.AlterField(
            model_name='defaultfood',
            name='ingredients',
            field=models.ManyToManyField(to=b'lunch.DefaultIngredient', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='category',
            field=models.ForeignKey(blank=True, to='lunch.FoodCategory', null=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='icon',
            field=models.ForeignKey(blank=True, to='lunch.Icon', null=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='ingredients',
            field=models.ManyToManyField(to=b'lunch.Ingredient', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='ingredientgroup',
            name='maximum',
            field=models.IntegerField(default=0, verbose_name=b'Maximum amount'),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='requestId',
            field=models.CharField(max_length=32, null=True, verbose_name=b'Request ID', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='userId',
            field=models.CharField(max_length=10, null=True, verbose_name=b'User ID', blank=True),
        ),
    ]
