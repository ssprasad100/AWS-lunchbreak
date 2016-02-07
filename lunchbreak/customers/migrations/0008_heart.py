# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0014_ingredientgroup_cost'),
        ('customers', '0007_useOriginal_costnodef'),
    ]

    operations = [
        migrations.CreateModel(
            name='Heart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(to='lunch.Store')),
                ('user', models.ForeignKey(to='customers.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='heart',
            unique_together=set([('user', 'store')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Received'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed'), (6, b'Not collected')]),
            preserve_default=True,
        ),
    ]
