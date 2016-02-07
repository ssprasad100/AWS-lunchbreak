# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lunch.models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=lunch.models.tokenGenerator, max_length=64)),
                ('device', models.CharField(max_length=128)),
                ('employee', models.ForeignKey(to='business.Employee')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StaffToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(default=lunch.models.tokenGenerator, max_length=64)),
                ('device', models.CharField(max_length=128)),
                ('employee', models.ForeignKey(to='business.Staff')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='staff',
            options={'verbose_name_plural': 'Staff'},
        ),
    ]
