# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_ingrm2m_foreign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedfood',
            name='order',
            field=models.ForeignKey(related_name='food', to='customers.Order'),
            preserve_default=True,
        ),
    ]
