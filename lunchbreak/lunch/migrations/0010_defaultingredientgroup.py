# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0009_foodtype_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultIngredientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('maximum', models.PositiveIntegerField(default=0, verbose_name=b'Maximum amount')),
                ('priority', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='store',
            field=models.ForeignKey(default=1, to='lunch.Store'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='defaultingredient',
            name='group',
            field=models.ForeignKey(to='lunch.DefaultIngredientGroup'),
            preserve_default=True,
        ),
    ]
