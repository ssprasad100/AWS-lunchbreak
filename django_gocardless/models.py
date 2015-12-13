from __future__ import unicode_literals

import urllib

import gocardless_pro
import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.crypto import get_random_string
from gocardless_pro.errors import GoCardlessProError

from .config import (CURRENCIES, MANDATE_STATUSES, PAYMENT_STATUSES,
                     PAYOUT_STATUSES, SCHEMES, SUBSCRIPTION_DAY_OF_MONTH,
                     SUBSCRIPTION_INTERVAL_UNIT, SUBSCRIPTION_MONTHS,
                     SUBSCRIPTION_STATUSES)
from .exceptions import (DjangoGoCardlessException,
                         ExchangeAuthorisationException)


class GCCacheMixin(object):

    '''
    Models that are cached for ease of use. These can be out of date with the
    GoCardless database and should therefore provide a way to sync with the
    GoCardless database. The `id` of the model should always be in sync if in
    the GoCardless database.
    '''

    def fetch(self, *args, **kwargs):
        raise NotImplementedError(
            '{cls} needs to implement required methods.'.format(
                cls=self.__class__.__name__
            )
        )


class GCOriginMixin(GCCacheMixin):

    '''
    Models that are not only cached for ease of use, but should be able to be
    created from this server using the GoCardless API.
    '''

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError(
            '{cls} needs to implement required methods.'.format(
                cls=cls.__name__
            )
        )

    def update(self, *args, **kwargs):
        raise NotImplementedError(
            '{cls} needs to implement required methods.'.format(
                cls=self.__class__.__name__
            )
        )


class Merchant(models.Model):

    '''
    GoCardless account accessed through OAuth. Other GoCardless models
    referencing a merchant mean that they belong to this merchant. If no
    merchant is referenced, the GoCardless information in the Django settings
    is used. Any GoCardless account is referred to as a merchant.

    This is not represented specifically anywhere in the GoCardless API. This
    is a virtual representation of the OAuth layer used to control other
    GoCardless accounts.
    '''

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


class Customer(models.Model, GCCacheMixin):

    '''
    Customer objects hold the contact details for a customer. A customer can
    have several customer bank accounts, which in turn can have several Direct
    Debit mandates.
    '''

    id = models.CharField(
        primary_key=True,
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
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Required unless family_name and given_name are provided.'
    )
    country_code = models.CharField(
        max_length=2,
        blank=True
    )
    created_at = models.DateTimeField(
        null=True
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


class CustomerBankAccount(models.Model, GCCacheMixin):

    '''
    Customer Bank Accounts hold the bank details of a customer. They always
    belong to a customer, and may be linked to several Direct Debit mandates.
    '''

    id = models.CharField(
        primary_key=True,
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
        null=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES
    )
    enabled = models.BooleanField(
        default=False
    )

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


class Mandate(models.Model, GCCacheMixin):

    '''
    Mandates represent the Direct Debit mandate with a customer.
    '''

    id = models.CharField(
        primary_key=True,
        blank=True,
        max_length=255
    )
    created_at = models.DateTimeField(
        null=True
    )
    next_possible_charge_date = models.DateField(
        null=True
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
        choices=MANDATE_STATUSES,
        default=MANDATE_STATUSES[0][0]
    )

    customer_bank_account = models.ForeignKey(
        CustomerBankAccount,
        null=True
    )

    def __unicode__(self):
        return self.id

    @classmethod
    def created(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[0][0]
        mandate.save()

    @classmethod
    def submitted(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[1][0]
        mandate.save()

    @classmethod
    def active(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[2][0]
        mandate.save()

    @classmethod
    def reinstated(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[2][0]
        mandate.save()

    @classmethod
    def transferred(cls, mandate, event, previous_customer_bank_account, new_customer_bank_account, **kwargs):
        # TODO Update customer bank account
        pass

    @classmethod
    def cancelled(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[4][0]
        mandate.save()

    @classmethod
    def failed(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[3][0]
        mandate.save()

    @classmethod
    def expired(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[5][0]
        mandate.save()

    @classmethod
    def resubmission_requested(cls, mandate, event, **kwargs):
        mandate.status = MANDATE_STATUSES[0][0]
        mandate.save()


class RedirectFlow(models.Model, GCOriginMixin):

    '''
    Redirect flows enable you to use GoCardless Pro's hosted payment pages to
    set up mandates with your customers. These pages are fully compliant and
    have been translated into Dutch, French, German, Italian, Portuguese,
    Spanish and Swedish.
    '''

    id = models.CharField(
        primary_key=True,
        max_length=255
    )
    created_at = models.DateTimeField(
        null=True
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


class Payout(models.Model, GCCacheMixin):

    '''
    Payouts represent transfers from GoCardless to a creditor. Each payout
    contains the funds collected from one or many payments. Payouts are created
    automatically after a payment has been successfully collected.
    '''

    id = models.CharField(
        primary_key=True,
        max_length=255
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    created_At = models.DateTimeField(
        null=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES
    )
    reference = models.CharField(
        max_length=140,
        blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=PAYOUT_STATUSES,
        blank=True
    )

    merchant = models.ForeignKey(
        Merchant,
        null=True
    )

    def __unicode__(self):
        return self.id


class Subscription(models.Model, GCOriginMixin):

    '''
    Subscriptions create payments according to a schedule.
    '''

    id = models.CharField(
        primary_key=True,
        max_length=255
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    count = models.PositiveIntegerField(
        null=True
    )
    created_At = models.DateTimeField(
        null=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES
    )
    day_of_month = models.IntegerField(
        choices=SUBSCRIPTION_DAY_OF_MONTH,
        null=True
    )
    end_date = models.DateField(
        null=True
    )
    interval = models.PositiveIntegerField(
        default=1
    )
    interval_unit = models.CharField(
        max_length=255,
        choices=SUBSCRIPTION_INTERVAL_UNIT
    )
    month = models.CharField(
        max_length=255,
        choices=SUBSCRIPTION_MONTHS,
        blank=True
    )
    name = models.CharField(
        max_length=255,
        blank=True
    )
    payment_reference = models.CharField(
        max_length=140,
        blank=True
    )
    start_date = models.DateField(
        null=True
    )
    status = models.CharField(
        max_length=255,
        choices=SUBSCRIPTION_STATUSES,
        default=SUBSCRIPTION_STATUSES[0][0]
    )

    mandate = models.ForeignKey(
        Mandate
    )

    def __unicode__(self):
        return self.name if self.name else self.id

    @property
    def upcoming_payments(self):
        raise NotImplementedError('Future payments are not yet implemented.')


class Payment(models.Model, GCOriginMixin):

    '''
    Payment objects represent payments from a customer to a creditor, taken
    against a Direct Debit mandate.
    '''

    id = models.CharField(
        primary_key=True,
        max_length=255
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    amount_refunded = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    charge_date = models.DateField(
        null=True
    )
    created_At = models.DateTimeField(
        null=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES
    )
    description = models.TextField(
        blank=True
    )
    reference = models.CharField(
        max_length=140,
        blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=PAYMENT_STATUSES,
        default=PAYMENT_STATUSES[0][0]
    )

    mandate = models.ForeignKey(
        Mandate,
        null=True
    )
    payout = models.ForeignKey(
        Payout,
        null=True
    )
    subscription = models.ForeignKey(
        Subscription,
        null=True
    )

    def __unicode__(self):
        return self.id
