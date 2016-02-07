# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0002_staff_emp_tokens'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stafftoken',
            old_name='employee',
            new_name='staff',
        ),
    ]
