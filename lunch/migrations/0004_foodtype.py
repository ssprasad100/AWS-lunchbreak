# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0003_order_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('icon', models.IntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='defaultfood',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='food',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='orderedfood',
            name='icon',
        ),
        migrations.AddField(
            model_name='defaultfood',
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='foodType',
            field=models.ForeignKey(to='lunch.FoodType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultingredient',
            name='icon',
            field=models.IntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')]),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='icon',
            field=models.IntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')]),
        ),
        migrations.DeleteModel(
            name='Icon',
        ),
    ]
