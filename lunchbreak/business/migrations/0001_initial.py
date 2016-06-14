# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dirtyfields.dirtyfields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('password_reset', models.CharField(default=None, max_length=64, null=True)),
                ('email', models.EmailField(help_text='Email address', unique=True, max_length=255)),
                ('first_name', models.CharField(help_text='First name', max_length=255)),
                ('last_name', models.CharField(help_text='Last name', max_length=255)),
                ('is_superuser', models.BooleanField(default=False)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='django_gocardless.Merchant', null=True)),
            ],
            options={
                'verbose_name_plural': 'Staff',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password_reset', models.CharField(default=None, max_length=64, null=True)),
                ('password', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('owner', models.BooleanField(default=False)),
                ('staff', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmployeeToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.IntegerField(default=2, verbose_name='Notification service', choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')])),
                ('registration_id', models.TextField(verbose_name='Registration ID', blank=True)),
                ('device', models.CharField(max_length=255)),
                ('identifier', models.CharField(max_length=255)),
                ('employee', models.ForeignKey(to='business.Employee')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
        migrations.CreateModel(
            name='StaffToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.IntegerField(default=2, verbose_name='Notification service', choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')])),
                ('registration_id', models.TextField(verbose_name='Registration ID', blank=True)),
                ('device', models.CharField(max_length=255)),
                ('identifier', models.CharField(max_length=255)),
                ('staff', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dirtyfields.dirtyfields.DirtyFieldsMixin),
        ),
    ]
