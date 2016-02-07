# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from customers.models import UserToken
from django.db import migrations, models


def hashIdentifiers(apps, schema_editor):
    for row in UserToken.objects.all():
        row.save(forceHashing=True)


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0023_user_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='identifier',
            field=models.CharField(max_length=255),
        ),
        migrations.RunPython(hashIdentifiers),
    ]
