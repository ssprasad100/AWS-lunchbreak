# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import private_media.storages


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0030_food_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original', models.ImageField(storage=private_media.storages.PrivateMediaStorage(), upload_to='storeheader')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='store',
            name='header',
            field=models.ForeignKey(to='lunch.StoreHeader', null=True),
        ),
    ]
