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
                ('orderedTime', models.DateTimeField(auto_now_add=True)),
                ('pickupTime', models.DateTimeField()),
                ('status', models.IntegerField(choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Accepted'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed')])),
                ('paid', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderedFood',
            fields=[
                ('food_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='lunch.Food')),
            ],
            options={
                'abstract': False,
            },
            bases=('lunch.food',),
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
            model_name='user',
            name='name',
            field=models.CharField(max_length=128, blank=True),
        ),
    ]
