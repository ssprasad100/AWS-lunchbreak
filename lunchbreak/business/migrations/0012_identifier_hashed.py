# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from business.models import EmployeeToken, StaffToken
from django.db import migrations, models


def hashIdentifiers(apps, schema_editor):
    for row in StaffToken.objects.all():
        row.save(force_hashing=True)

    for row in EmployeeToken.objects.all():
        row.save(force_hashing=True)


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0011_service_inactive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetoken',
            name='identifier',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='identifier',
            field=models.CharField(max_length=255),
        ),
        migrations.RunPython(hashIdentifiers),
    ]
