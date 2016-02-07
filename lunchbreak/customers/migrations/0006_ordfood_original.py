# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0007_ingredientrelation'),
        ('customers', '0005_amount_decimal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedfood',
            name='category',
        ),
        migrations.RemoveField(
            model_name='orderedfood',
            name='foodType',
        ),
        migrations.RemoveField(
            model_name='orderedfood',
            name='name',
        ),
        migrations.RemoveField(
            model_name='orderedfood',
            name='store',
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='original',
            field=models.ForeignKey(default=4, to='lunch.Food'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='cost',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderedfood',
            name='order',
            field=models.ForeignKey(to='customers.Order'),
            preserve_default=True,
        ),
    ]
