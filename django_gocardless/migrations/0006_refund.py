# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_gocardless.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0005_auto_20151213_1316'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(null=True, max_digits=12, decimal_places=2)),
                ('created_At', models.DateTimeField(null=True)),
                ('currency', models.CharField(blank=True, max_length=3, choices=[(b'EUR', b'Euro'), (b'GBP', b'British Pound'), (b'SEK', b'Swedish Krona')])),
                ('reference', models.CharField(max_length=140, blank=True)),
                ('payment', models.ForeignKey(to='django_gocardless.Payment', null=True)),
            ],
            bases=(models.Model, django_gocardless.models.GCCacheMixin),
        ),
    ]
