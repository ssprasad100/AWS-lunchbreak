# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0006_remove_ingredients'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultIngredientRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typical', models.BooleanField(default=False)),
                ('food', models.ForeignKey(to='lunch.DefaultFood')),
                ('ingredient', models.ForeignKey(to='lunch.DefaultIngredient')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typical', models.BooleanField(default=False)),
                ('food', models.ForeignKey(to='lunch.Food')),
                ('ingredient', models.ForeignKey(to='lunch.Ingredient')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.DefaultIngredient', null=True, through='lunch.DefaultIngredientRelation', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient', null=True, through='lunch.IngredientRelation', blank=True),
            preserve_default=True,
        ),
    ]
