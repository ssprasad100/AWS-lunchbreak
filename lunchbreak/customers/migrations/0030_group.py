# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0029_orderedfood_rename'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('payment', models.IntegerField(default=0, choices=[(0, b'Separate'), (1, b'Leader')])),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('leader', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='customers.Group')),
                ('user', models.ForeignKey(to='customers.User')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(to='customers.User', through='customers.Membership'),
        ),
    ]
