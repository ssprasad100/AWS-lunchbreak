# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-06-22 15:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_sms', '0001_initial'),
        ('django_gocardless', '0001_initial'),
        ('lunch', '0001_initial'),
        ('payconiq', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0007_alter_validators_add_error_messages'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryorder',
            name='store',
            field=models.ForeignKey(help_text='Winkel.', on_delete=django.db.models.deletion.CASCADE, to='lunch.Store', verbose_name='winkel'),
        ),
        migrations.AddField(
            model_name='temporaryorder',
            name='user',
            field=models.ForeignKey(help_text='Gebruiker.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='gebruiker'),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='redirectflow',
            field=models.ForeignKey(help_text='GoCardless doorverwijzing voor het tekenen van een mandaat.', on_delete=django.db.models.deletion.CASCADE, to='django_gocardless.RedirectFlow', verbose_name='doorverwijzing'),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='store',
            field=models.ForeignKey(help_text='Winkel.', on_delete=django.db.models.deletion.CASCADE, to='lunch.Store', verbose_name='winkel'),
        ),
        migrations.AddField(
            model_name='paymentlink',
            name='user',
            field=models.ForeignKey(help_text='Gebruiker.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='gebruiker'),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='ingredients',
            field=models.ManyToManyField(blank=True, help_text='Ingrediënten.', to='lunch.Ingredient', verbose_name='ingrediënten'),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='original',
            field=models.ForeignKey(blank=True, help_text='Origineel etenswaar.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='lunch.Food', verbose_name='origineel etenswaar'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.ForeignKey(blank=True, help_text='Leveringsadres.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='customers.Address', verbose_name='leveringsadres'),
        ),
        migrations.AddField(
            model_name='order',
            name='group_order',
            field=models.ForeignKey(blank=True, help_text='Groepsbestelling waartoe bestelling behoort.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='customers.GroupOrder', verbose_name='groepsbestelling'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(blank=True, help_text='Betaling.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_gocardless.Payment', verbose_name='betaling'),
        ),
        migrations.AddField(
            model_name='order',
            name='store',
            field=models.ForeignKey(help_text='Winkel.', on_delete=django.db.models.deletion.CASCADE, to='lunch.Store', verbose_name='winkel'),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payconiq.Transaction'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(help_text='Gebruiker.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='gebruiker'),
        ),
        migrations.AddField(
            model_name='heart',
            name='store',
            field=models.ForeignKey(help_text='Winkel.', on_delete=django.db.models.deletion.CASCADE, to='lunch.Store', verbose_name='winkel'),
        ),
        migrations.AddField(
            model_name='heart',
            name='user',
            field=models.ForeignKey(help_text='Gebruiker.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='gebruiker'),
        ),
        migrations.AddField(
            model_name='grouporder',
            name='group',
            field=models.ForeignKey(help_text='Groep.', on_delete=django.db.models.deletion.CASCADE, related_name='group_orders', to='customers.Group', verbose_name='groep'),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, help_text='Groepsleden.', related_name='store_groups', to=settings.AUTH_USER_MODEL, verbose_name='leden'),
        ),
        migrations.AddField(
            model_name='group',
            name='store',
            field=models.ForeignKey(help_text='Winkel verbonden met deze groep.', on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='lunch.Store', verbose_name='winkel'),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(help_text='Gebruiker.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='gebruiker'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='paymentlinks',
            field=models.ManyToManyField(blank=True, help_text='Getekende mandaten.', through='customers.PaymentLink', to='lunch.Store', verbose_name='getekende mandaten'),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.OneToOneField(help_text='Telefoonnummer.', on_delete=django.db.models.deletion.CASCADE, to='django_sms.Phone', verbose_name='telefoonnummer'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='ConfirmedOrder',
            fields=[
            ],
            options={
                'verbose_name': 'bevestigde bestelling',
                'proxy': True,
                'verbose_name_plural': 'bevestigde bestellingen',
            },
            bases=('customers.order',),
        ),
        migrations.AlterUniqueTogether(
            name='temporaryorder',
            unique_together=set([('user', 'store')]),
        ),
        migrations.AlterUniqueTogether(
            name='paymentlink',
            unique_together=set([('user', 'store')]),
        ),
        migrations.AlterUniqueTogether(
            name='heart',
            unique_together=set([('user', 'store')]),
        ),
        migrations.AlterUniqueTogether(
            name='grouporder',
            unique_together=set([('group', 'date')]),
        ),
    ]
