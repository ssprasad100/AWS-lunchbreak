# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0007_ingredientrelation'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='defaultingredientrelation',
            unique_together=set([('food', 'ingredient')]),
        ),
        migrations.AlterUniqueTogether(
            name='ingredientrelation',
            unique_together=set([('food', 'ingredient')]),
        ),
    ]
