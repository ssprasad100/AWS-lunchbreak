# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0006_storenumber_pos'),
    ]

    operations = [
        migrations.CreateModel(
            name='HolidayPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=128)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('closed', models.BooleanField(default=True)),
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.IntegerField(choices=[(0, b'Maandag'), (1, b'Dinsdag'), (2, b'Woensdag'), (3, b'Donderdeg'), (4, b'Vrijdag'), (5, b'Zaterdag'), (6, b'Zondag')])),
                ('opening', models.TimeField()),
                ('closing', models.TimeField()),
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
                'verbose_name_plural': 'Opening hours',
            },
            bases=(models.Model,),
        ),
    ]
