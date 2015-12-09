from __future__ import unicode_literals

import urllib

import gocardless_pro
import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.crypto import get_random_string
from gocardless_pro.errors import GoCardlessProError

from .config import MANDATE_STATUSES, SCHEMES
from .exceptions import (DjangoGoCardlessException,
                         ExchangeAuthorisationException)


class Merchant(models.Model):
    access_token = models.CharField(
        max_length=255
    )
    organisation_id = models.CharField(
        max_length=255
    )
    state = models.CharField(
        max_length=56,
        help_text='CSRF Token'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __unicode__(self):
        return self.organisation_id

    @classmethod
    def authorisation_link(cls, email=None, initial_view='signup'):
        state = get_random_string(length=56)

        merchant = cls.objects.create(
            state=state
        )

        params = {
            'response_type': 'code',
            'client_id': settings.GOCARDLESS['app']['client_id'],
            'scope': 'full_access',
            'redirect_uri': settings.GOCARDLESS['app']['redirect_uri'],
            'state': merchant.state,
            'initial_view': initial_view
        }

        if email is not None:
            params['prefill[email]'] = email

        return '{baseurl}?{params}'.format(
            baseurl=settings.GOCARDLESS['app']['oauth_baseurl'][
                settings.GOCARDLESS['environment']],
            params=urllib.urlencode(params)
        )

    def exchange_authorisation(self, code):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.GOCARDLESS['app']['redirect_url'],
            'client_id': settings.GOCARDLESS['app']['client_id'],
            'client_secret': settings.GOCARDLESS['app']['client_secret']
        }
        response = requests.post(
            '{baseurl}{location}'.format(
                baseurl=settings.GOCARDLESS['app']['oauth_baseurl'][
                    settings.GOCARDLESS['environment']],
                location='/oauth/access_token'
            ),
            data=data
        )

        try:
            response_data = response.json()

            if ('error' not in response_data and
                    response_data.get('scope', None) == 'full_access'):
                self.access_token = response_data['access_token']
                self.organisation_id = response_data['organisation_id']
                self.save()
            else:
                raise ExchangeAuthorisationException()
        except ValueError:
            raise ExchangeAuthorisationException()


class Customer(models.Model):
    id = models.CharField(
        primary_key=True,
        blank=True,
        null=False,
        max_length=255
    )
    address_line1 = models.CharField(
        max_length=255,
        blank=True
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True
    )
    address_line3 = models.CharField(
        max_length=255,
        blank=True
    )
    city = models.CharField(
        max_length=255,
        blank=True
    )
    # Required unless family_name and given_name are provided.
    company_name = models.CharField(
        max_length=255,
        blank=True
    )
    country_code = models.CharField(
        max_length=2,
        blank=True
    )
    created_at = models.DateTimeField(
        null=True,
        blank=True
    )
    email = models.EmailField(
        blank=True
    )
    family_name = models.CharField(
        max_length=255,
        blank=True
    )
    first_name = models.CharField(
        max_length=255,
        blank=True
    )
    language = models.CharField(
        max_length=2,
        blank=True
    )
    postal_code = models.CharField(
        max_length=255,
        blank=True
    )
    region = models.CharField(
        max_length=255,
        blank=True
    )
    swedish_identifity_number = models.CharField(
        max_length=255,
        blank=True
    )

    merchant = models.ForeignKey(
        Merchant,
        null=True,
        blank=True,
        help_text='Merchant if not a direct customer.'
    )

    def __unicode__(self):
        if not self.company_name:
            return self.company_name
        else:
            return self.family_name + ' ' + self.first_name


class CustomerBankAccount(models.Model):
    id = models.CharField(
        primary_key=True,
        blank=True,
        null=False,
        max_length=255
    )
    account_holder_name = models.CharField(
        max_length=18
    )
    account_number_ending = models.CharField(
        max_length=2
    )
    bank_name = models.CharField(
        max_length=255
    )
    country_code = models.CharField(
        max_length=2
    )
    created_at = models.DateTimeField(
        null=True,
        blank=True
    )
    currency = models.CharField(
        max_length=3
    )
    enabled = models.BooleanField()

    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True
    )

    def __unicode__(self):
        return '{name} ({id})'.format(
            name=self.account_holder_name,
            id=self.id
        )


class Mandate(models.Model):
    id = models.CharField(
        primary_key=True,
        blank=True,
        max_length=255
    )
    created_at = models.DateTimeField(
        null=True,
        blank=True
    )
    next_possible_charge_date = models.DateField(
        null=True,
        blank=True
    )
    reference = models.CharField(
        max_length=255,
        blank=True
    )
    scheme = models.CharField(
        max_length=255,
        blank=True,
        choices=SCHEMES
    )
    status = models.CharField(
        max_length=255,
        blank=True,
        choices=MANDATE_STATUSES
    )

    customer_bank_account = models.ForeignKey(
        CustomerBankAccount,
        null=True
    )

    def __unicode__(self):
        return self.id

    @classmethod
    def created(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[0][0]
        instance.save()

    @classmethod
    def submitted(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[1][0]
        instance.save()

    @classmethod
    def active(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[2][0]
        instance.save()

    @classmethod
    def reinstated(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[2][0]
        instance.save()

    @classmethod
    def transferred(cls, instance, event, **kwargs):
        # TODO Update customer_bank_account
        pass

    @classmethod
    def cancelled(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[4][0]
        instance.save()

    @classmethod
    def failed(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[3][0]
        instance.save()

    @classmethod
    def expired(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[5][0]
        instance.save()

    @classmethod
    def resubmission_requested(cls, instance, event, **kwargs):
        instance.status = MANDATE_STATUSES[0][0]
        instance.save()


class RedirectFlow(models.Model):
    id = models.CharField(
        primary_key=True,
        null=False,
        max_length=255
    )
    created_at = models.DateTimeField(
        null=True,
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    redirect_url = models.URLField(
        blank=True
    )
    scheme = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=SCHEMES
    )
    session_token = models.CharField(
        max_length=255,
        blank=True
    )
    redirect_url = models.URLField(
        blank=True
    )

    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True
    )
    customer_bank_account = models.ForeignKey(
        CustomerBankAccount,
        null=True,
        blank=True
    )
    mandate = models.ForeignKey(
        Mandate,
        null=True,
        blank=True
    )

    @classmethod
    def create(cls, description=''):
        redirectflow = cls(
            session_token='SESS_{random}'.format(
                random=get_random_string(length=56)
            ),
            description=description
        )

        client = gocardless_pro.Client(
            access_token=settings.GOCARDLESS['access_token'],
            environment=settings.GOCARDLESS['environment']
        )

        protocol = 'https' if settings.SSL else 'http'
        response = client.redirect_flows.create(
            params={
                'session_token': redirectflow.session_token,
                'description': description,
                'success_redirect_url': '{protocol}://{baseurl}{path}'.format(
                    protocol=protocol,
                    baseurl=settings.HOST,
                    path=reverse('gocardless_redirectflow_success')
                )
            }
        )

        redirectflow.id = response.id
        redirectflow.description = response.description
        redirectflow.scheme = response.scheme
        redirectflow.redirect_url = response.redirect_url
        redirectflow.created_at = response.created_at

        redirectflow.save()

        return redirectflow

    def complete(self):
        client = gocardless_pro.Client(
            access_token=settings.GOCARDLESS['access_token'],
            environment=settings.GOCARDLESS['environment']
        )

        try:
            response = client.redirect_flows.complete(
                self.id,
                params={
                    'session_token': self.session_token
                }
            )
        except GoCardlessProError as e:
            raise DjangoGoCardlessException(e)

        try:
            customer = response.links.customer

            if customer:
                self.customer, created = Customer.objects.get_or_create(
                    id=customer
                )
        except AttributeError:
            pass

        try:
            customer_bank_account = response.links.customer_bank_account

            if customer_bank_account:
                self.customer_bank_account, created = CustomerBankAccount.objects.get_or_create(
                    id=customer_bank_account
                )
        except AttributeError:
            pass

        try:
            mandate = response.links.mandate

            if mandate:
                self.mandate, created = Mandate.objects.get_or_create(
                    id=mandate
                )
        except AttributeError:
            pass

        self.save()

    def __unicode__(self):
        return self.id
