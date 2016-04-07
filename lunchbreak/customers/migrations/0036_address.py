# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import dirtyfields.dirtyfields


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0035_payment_blank'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=255)),
                ('province', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('postcode', models.CharField(max_length=20, verbose_name='Postal code')),
                ('street', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=10)),
                ('latitude', models.DecimalField(max_digits=10, decimal_places=7)),
                ('longitude', models.DecimalField(max_digits=10, decimal_places=7)),
                ('deleted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to='customers.User')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='customers.Address', null=True),
        ),
    ]
