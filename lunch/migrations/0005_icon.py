# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0004_foodcategory'),
    ]

    operations = [
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
        migrations.AlterModelOptions(
            name='defaultfoodcategory',
            options={'verbose_name_plural': 'Default food categories'},
        ),
        migrations.AlterModelOptions(
            name='foodcategory',
            options={'verbose_name_plural': 'Food categories'},
        ),
        migrations.AlterModelOptions(
            name='storecategory',
            options={'verbose_name_plural': 'Store categories'},
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='icon',
            field=models.ForeignKey(to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultingredient',
            name='icon',
            field=models.ForeignKey(to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='icon',
            field=models.ForeignKey(to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='icon',
            field=models.ForeignKey(to='lunch.Icon', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storecategory',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
