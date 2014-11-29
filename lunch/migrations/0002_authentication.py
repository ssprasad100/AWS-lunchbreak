# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lunch.models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0001_initial'),
    ]

    operations = [
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
                ('name', models.CharField(max_length=128)),
                ('digitsId', models.CharField(unique=True, max_length=10)),
                ('phone', models.CharField(max_length=17, serialize=False, primary_key=True)),
                ('createdAt', models.DateField(auto_now=True)),
                ('confirmed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='token',
            name='digitsId',
            field=models.ForeignKey(to='lunch.User', db_column=b'digitsId'),
            preserve_default=True,
        ),
    ]
