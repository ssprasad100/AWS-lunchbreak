# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0040_orderedfood_rename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='food',
            old_name='canComment',
            new_name='commentable',
        ),
        migrations.RenameField(
            model_name='food',
            old_name='foodType',
            new_name='foodtype',
        ),
        migrations.RenameField(
            model_name='food',
            old_name='ingredient_groups',
            new_name='ingredientgroups',
        ),
        migrations.RenameField(
            model_name='food',
            old_name='lastModified',
            new_name='modified',
        ),
        migrations.RenameField(
            model_name='food',
            old_name='minDays',
            new_name='preorder_days',
        ),
        migrations.RenameField(
            model_name='foodtype',
            old_name='inputType',
            new_name='inputtype',
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='lastModified',
            new_name='modified',
        ),
        migrations.RenameField(
            model_name='ingredientgroup',
            old_name='costCalculation',
            new_name='calculation',
        ),
        migrations.RenameField(
            model_name='ingredientgroup',
            old_name='foodType',
            new_name='foodtype',
        ),
        migrations.RenameField(
            model_name='quantity',
            old_name='foodType',
            new_name='foodtype',
        ),
        migrations.RenameField(
            model_name='quantity',
            old_name='amountMax',
            new_name='max',
        ),
        migrations.RenameField(
            model_name='quantity',
            old_name='amountMin',
            new_name='min',
        ),
        migrations.RenameField(
            model_name='quantity',
            old_name='lastModified',
            new_name='modified',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='lastModified',
            new_name='modified',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='orderTime',
            new_name='preorder_time',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='maxSeats',
            new_name='seats_max',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='minTime',
            new_name='wait',
        ),
        migrations.AlterUniqueTogether(
            name='quantity',
            unique_together=set([('foodtype', 'store')]),
        ),
    ]
