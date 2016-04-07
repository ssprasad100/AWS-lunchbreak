# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0044_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opening_day', models.PositiveSmallIntegerField(choices=[(0, b'Zondag'), (1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag')])),
                ('closing_day', models.PositiveSmallIntegerField(choices=[(0, b'Zondag'), (1, b'Maandag'), (2, b'Dinsdag'), (3, b'Woensdag'), (4, b'Donderdag'), (5, b'Vrijdag'), (6, b'Zaterdag')])),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='store',
            name='regions',
            field=models.ManyToManyField(help_text='Active delivery regions.', to='lunch.Region'),
        ),
        migrations.AddField(
            model_name='deliveryperiod',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
    ]
