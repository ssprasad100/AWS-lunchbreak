# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-24 13:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0008_auto_20161005_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetoken',
            name='employee',
            field=models.ForeignKey(help_text='Werknemer.', on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='business.Employee', verbose_name='werknemer'),
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='staff',
            field=models.ForeignKey(help_text='Personeel.', on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='business.Staff', verbose_name='personeel'),
        ),
    ]