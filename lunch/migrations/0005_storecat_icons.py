# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0004_foodtype_inptypenull'),
    ]

    operations = [
        migrations.AddField(
            model_name='storecategory',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Onbekend'), (100, b'Slager'), (101, b'Bakker'), (102, b'Broodjeszaak'), (200, b'Tomaten'), (300, b'Broodje')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultingredient',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Onbekend'), (100, b'Slager'), (101, b'Bakker'), (102, b'Broodjeszaak'), (200, b'Tomaten'), (300, b'Broodje')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Onbekend'), (100, b'Slager'), (101, b'Bakker'), (102, b'Broodjeszaak'), (200, b'Tomaten'), (300, b'Broodje')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Onbekend'), (100, b'Slager'), (101, b'Bakker'), (102, b'Broodjeszaak'), (200, b'Tomaten'), (300, b'Broodje')]),
            preserve_default=True,
        ),
    ]
