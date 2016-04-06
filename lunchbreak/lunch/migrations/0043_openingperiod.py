# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0042_foodcat_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpeningPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opening_day', models.PositiveSmallIntegerField(choices=[(0, b'Zondag'), (1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag')])),
                ('closing_day', models.PositiveSmallIntegerField(choices=[(0, b'Zondag'), (1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag')])),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
                ('store', models.ForeignKey(to='lunch.Store')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='openinghours',
            name='store',
        ),
        migrations.DeleteModel(
            name='OpeningHours',
        ),
    ]
