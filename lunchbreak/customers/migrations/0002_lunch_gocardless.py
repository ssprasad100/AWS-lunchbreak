# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_gocardless', '0001_initial'),
        ('customers', '0001_initial'),
        ('lunch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='paymentlinks',
            field=models.ManyToManyField(to='lunch.Store', through='customers.PaymentLink', blank=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='redirectflow',
            field=models.ForeignKey(to='django_gocardless.RedirectFlow'),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='ingredients',
            field=models.ManyToManyField(to='lunch.Ingredient', blank=True),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='order',
            field=models.ForeignKey(to='customers.Order'),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='original',
            field=models.ForeignKey(to='lunch.Food'),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='customers.Address', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='django_gocardless.Payment', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='reservation',
            field=models.OneToOneField(null=True, blank=True, to='customers.Reservation'),
        ),
        migrations.AddField(
            model_name='order',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
        migrations.AddField(
            model_name='membership',
            name='group',
            field=models.ForeignKey(to='customers.Group'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(to='customers.User'),
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
            field=models.ForeignKey(blank=True, to='customers.Membership', null=True),
        ),
        migrations.AddField(
            model_name='invite',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
        migrations.AddField(
            model_name='heart',
            name='store',
            field=models.ForeignKey(to='lunch.Store'),
        ),
        migrations.AddField(
            model_name='heart',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(to='customers.User', through='customers.Membership'),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(to='customers.User'),
        ),
        migrations.AlterUniqueTogether(
            name='paymentlink',
            unique_together=set([('user', 'store')]),
        ),
        migrations.AlterUniqueTogether(
            name='invite',
            unique_together=set([('group', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='heart',
            unique_together=set([('user', 'store')]),
        ),
    ]
