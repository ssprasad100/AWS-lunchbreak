# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0003_redirectflow_merchant'),
        ('lunch', '0041_rename'),
        ('customers', '0033_user_no_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('redirectflow', models.ForeignKey(to='django_gocardless.RedirectFlow')),
                ('store', models.ForeignKey(to='lunch.Store')),
                ('user', models.ForeignKey(to='customers.User')),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='paid',
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='django_gocardless.Payment', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.IntegerField(default=0, choices=[(0, b'Cash'), (1, b'GoCardless')]),
        ),
        migrations.AddField(
            model_name='user',
            name='paymentlinks',
            field=models.ManyToManyField(to='lunch.Store', through='customers.PaymentLink', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='paymentlink',
            unique_together=set([('user', 'store')]),
        ),
    ]
