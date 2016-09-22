# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return

    Phone = apps.get_model('django_sms.Phone')
    User = apps.get_model('customers.User')

    for user in User.objects.all():
        user.phone_link = Phone.objects.create(
            phone=user.phone,
            confirmed_at=user.confirmed_at,
        )
        user.save()

        # auto_now_add overrides arguments at creation
        if user.confirmed_at is not None:
            Phone.objects.filter(
                pk=user.phone_link_id
            ).update(
                created_at=user.confirmed_at
            )


class Migration(migrations.Migration):

    dependencies = [
        ('django_sms', '0001_initial'),
        ('customers', '0007_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='digits_id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='request_id',
        ),
        migrations.AddField(
            model_name='user',
            name='phone_link',
            field=models.OneToOneField(null=True, to='django_sms.Phone'),
        ),
        migrations.RunPython(forwards)
    ]
