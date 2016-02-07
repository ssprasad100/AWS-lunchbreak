# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0016_ingrgroup_foodtype_min'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultfood',
            name='cost',
            field=models.DecimalField(max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultfood',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultfoodcategory',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultingredient',
            name='cost',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultingredient',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultingredientgroup',
            name='cost',
            field=models.DecimalField(default=-1, max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultingredientgroup',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='food',
            name='cost',
            field=models.DecimalField(max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='food',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodcategory',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='inputType',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Aantal'), (1, b'Gewicht'), (2, b'Aantal en gewicht')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='quantifier',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='holidayperiod',
            name='description',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='cost',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingredientgroup',
            name='cost',
            field=models.DecimalField(default=-1, max_digits=7, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingredientgroup',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='openinghours',
            name='day',
            field=models.PositiveIntegerField(choices=[(0, b'Zondag'), (1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='city',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='country',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='province',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='street',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storecategory',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
