# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-06-22 15:39
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forward',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('group', models.CharField(max_length=191)),
                ('json', jsonfield.fields.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
