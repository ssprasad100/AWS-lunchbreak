# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0021_food_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quantity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amountMin', models.DecimalField(default=1, max_digits=7, decimal_places=3)),
                ('amountMax', models.DecimalField(default=10, max_digits=7, decimal_places=3)),
                ('lastModified', models.DateTimeField(auto_now=True)),
                ('foodType', models.ForeignKey(to='lunch.FoodType')),
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='quantity',
            unique_together=set([('foodType', 'store')]),
        ),
        migrations.AlterField(
            model_name='store',
            name='minTime',
            field=models.PositiveIntegerField(default=60),
            preserve_default=True,
        ),
    ]
