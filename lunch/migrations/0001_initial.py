# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
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
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
