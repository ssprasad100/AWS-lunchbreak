# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0030_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Waiting'), (1, b'Accepted'), (2, b'Declined'), (3, b'Removed')])),
            ],
        ),
        migrations.RenameField(
            model_name='group',
            old_name='payment',
            new_name='billing',
        ),
        migrations.AddField(
            model_name='invite',
            name='group',
            field=models.ForeignKey(to='customers.Group'),
        ),
        migrations.AddField(
            model_name='invite',
            name='invited_by',
            field=models.ForeignKey(related_name='sent_invites', to='customers.User'),
        ),
        migrations.AddField(
            model_name='invite',
            name='membership',
            field=models.ForeignKey(to='customers.Membership', null=True),
        ),
        migrations.AddField(
            model_name='invite',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
    ]
