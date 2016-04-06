# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0043_openingperiod'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('country', models.PositiveSmallIntegerField(choices=[(0, b'Belgium'), (1, b'The Netherlands'), (2, b'Luxemburg'), (3, b'France'), (4, b'Germany')])),
                ('postcode', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('country', 'postcode')]),
        ),
    ]
