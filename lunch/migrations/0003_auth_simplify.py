# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0002_authentication'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='digitsId',
        ),
        migrations.RemoveField(
            model_name='user',
            name='createdAt',
        ),
        migrations.RemoveField(
            model_name='user',
            name='digitsId',
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.ForeignKey(db_column=b'phone', default='MIGRATION FAIL', to='lunch.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='confirmedAt',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='requestId',
            field=models.CharField(max_length=32, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='userId',
            field=models.CharField(max_length=10, null=True, blank=True),
            preserve_default=True,
        ),
    ]
