# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0008_mintime'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodtype',
            name='inputType',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Aantal'), (1, b'Gewicht')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtype',
            name='quantifier',
            field=models.CharField(default='Kwantor', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='defaultingredient',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')]),
        ),
        migrations.AlterField(
            model_name='foodtype',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')]),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='icon',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Icoontje 0'), (1, b'Icoontje 1'), (2, b'Icoontje 2'), (3, b'Icoontje 3'), (4, b'Icoontje 4'), (5, b'Icoontje 5')]),
        ),
        migrations.AlterField(
            model_name='openinghours',
            name='day',
            field=models.PositiveIntegerField(choices=[(0, b'Maandag'), (1, b'Dinsdag'), (2, b'Woensdag'), (3, b'Donderdeg'), (4, b'Vrijdag'), (5, b'Zaterdag'), (6, b'Zondag')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Placed'), (1, b'Denied'), (2, b'Accepted'), (3, b'Started'), (4, b'Waiting'), (5, b'Completed')]),
        ),
    ]
