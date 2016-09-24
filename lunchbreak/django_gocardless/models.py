import urllib
from datetime import timedelta

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

from .config import (CURRENCIES, MANDATE_STATUSES, PAYMENT_STATUSES,
                     PAYOUT_STATUSES, SCHEMES, SUBSCRIPTION_DAY_OF_MONTH,
                     SUBSCRIPTION_INTERVAL_UNIT, SUBSCRIPTION_MONTHS,
                     SUBSCRIPTION_STATUSES)
from .exceptions import ExchangeAuthorisationError
from .mixins import GCCacheMixin, GCCreateMixin, GCCreateUpdateMixin
from .utils import model_from_links


class Merchant(models.Model):

    """
    GoCardless account accessed through OAuth. Other GoCardless models
    referencing a merchant mean that they belong to this merchant. If no
    merchant is referenced, the GoCardless information in the Django settings
    is used. Any GoCardless account is referred to as a merchant.

    This is not represented specifically anywhere in the GoCardless API. This
    is a virtual representation of the OAuth layer used to control other
    GoCardless accounts.
    """

    access_token = models.CharField(
        max_length=255,
        blank=True
    )
    organisation_id = models.CharField(
        max_length=255,
        blank=True
    )
    state = models.CharField(
        max_length=56,
        help_text='CSRF Token',
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.organisation_id if self.organisation_id else _('In progress')

    @property
    def confirmed(self):
        return bool(self.organisation_id)

    @staticmethod
    def get_redirect_uri():
        return '{protocol}://{domain}{path}'.format(
            protocol='https' if settings.SSL else 'http',
            domain=settings.GOCARDLESS['app']['merchant']['exchange_domain'],
            path=reverse('gocardless-redirect')
        )

    @classmethod
    def authorisation_link(cls, email=None, initial_view='signup'):
        state = None
        while state is None or cls.objects.filter(state=state).count() > 0:
            state = get_random_string(length=56)

        # Delete Merchants that have not been confirmed
        cls.objects.filter(
            created_at__lt=timezone.now() - timedelta(hours=1),
            access_token='',
            organisation_id=''
        ).delete()
        merchant = cls.objects.create(
            state=state
        )

        params = {
            'response_type': 'code',
            'client_id': settings.GOCARDLESS['app']['client_id'],
            'scope': 'read_write',
            'redirect_uri': cls.get_redirect_uri(),
            'state': merchant.state,
            'initial_view': initial_view
        }

        if email is not None:
            params['prefill[email]'] = email

        url = '{baseurl}/oauth/authorize?{params}'.format(
            baseurl=settings.GOCARDLESS['app']['oauth_baseurl'][
                settings.GOCARDLESS['environment']],
            params=urllib.parse.urlencode(params)
        )

        return (merchant, url)

    @classmethod
    def exchange_authorisation(cls, state, code):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': cls.get_redirect_uri(),
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

            if 'error' in response_data:
                raise ExchangeAuthorisationError(
                    response_data['error']
                )

            if response_data.get('scope', None) == 'read_write':
                merchant = cls.objects.get(state=state)
                merchant.state = ''
                merchant.access_token = response_data['access_token']
                merchant.organisation_id = response_data['organisation_id']
                merchant.save()
                return merchant
            else:
                raise ExchangeAuthorisationError(
                    'Scope not read_write.'
                )
        except cls.DoesNotExist:
            raise ExchangeAuthorisationError()
        except ValueError:
            raise ExchangeAuthorisationError()


class Customer(models.Model, GCCacheMixin):

    """
    Customer objects hold the contact details for a customer. A customer can
    have several customer bank accounts, which in turn can have several Direct
    Debit mandates.
    """

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
    swedish_identity_number = models.CharField(
        max_length=255,
        blank=True
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Merchant if not a direct customer.'
    )

    def __str__(self):
        if not self.company_name:
            if not self.family_name and not self.first_name:
                return self.family_name + ' ' + self.first_name
            else:
                return self.id
        else:
            return self.company_name


class CustomerBankAccount(models.Model, GCCacheMixin):

    """
    Customer Bank Accounts hold the bank details of a customer. They always
    belong to a customer, and may be linked to several Direct Debit mandates.
    """

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
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{name} ({id})'.format(
            name=self.account_holder_name,
            id=self.id
        )

    @cached_property
    def merchant(self):
        return self.customer.merchant if self.customer is not None else None


class Mandate(models.Model, GCCacheMixin):

    """
    Mandates represent the Direct Debit mandate with a customer.
    """

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

    customer_bank_account = models.OneToOneField(
        CustomerBankAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.id

    @cached_property
    def merchant(self):
        try:
            if self.redirectflow is not None:
                return self.redirectflow.merchant
        except RedirectFlow.DoesNotExist:
            pass
        return self.customer_bank_account.merchant\
            if self.customer_bank_account is not None\
            else None

    @staticmethod
    def created(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[0][0]
        mandate.save()

    @staticmethod
    def submitted(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[1][0]
        mandate.save()

    @staticmethod
    def active(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[2][0]
        mandate.save()

    @staticmethod
    def reinstated(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[2][0]
        mandate.save()

    @staticmethod
    def transferred(sender, mandate, event, previous_customer_bank_account,
                    new_customer_bank_account, **kwargs):
        # TODO Update customer bank account
        pass

    @staticmethod
    def cancelled(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[4][0]
        mandate.save()

    @staticmethod
    def failed(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[3][0]
        mandate.save()

    @staticmethod
    def expired(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[5][0]
        mandate.save()

    @staticmethod
    def resubmission_requested(sender, mandate, event, merchant=None, **kwargs):
        mandate.status = MANDATE_STATUSES[0][0]
        mandate.save()


class RedirectFlow(models.Model, GCCreateMixin):

    """
    Redirect flows enable you to use GoCardless Pro's hosted payment pages to
    set up mandates with your customers. These pages are fully compliant and
    have been translated into Dutch, French, German, Italian, Portuguese,
    Spanish and Swedish.
    """

    create_fields = {
        'required': [
            'session_token',
            'success_redirect_url',
        ],
        'optional': [
            'description',
            'scheme',
        ]
    }

    ignore_fields = [
        'completion_redirect_url'
    ]

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
        blank=True,
        help_text=(
            'The URL of the hosted payment pages for this redirect flow. '
            'This is the URL you should redirect your customer to.'
        )
    )

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    customer_bank_account = models.OneToOneField(
        CustomerBankAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    mandate = models.OneToOneField(
        Mandate,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    completion_redirect_url = models.URLField(
        null=True,
        help_text='After completion of the RedirectFlow where to redirect the user to.'
    )

    @cached_property
    def is_completed(self):
        return self.customer is not None and \
            self.customer_bank_account is not None and \
            self.mandate is not None

    @classmethod
    def create(cls, description='', merchant=None, completion_redirect_url=None,
               *args, **kwargs):
        redirectflow = cls(
            session_token='SESS_{random}'.format(
                random=get_random_string(length=56)
            ),
            description=description,
            merchant=merchant,
            completion_redirect_url=completion_redirect_url
        )

        params = {
            'session_token': redirectflow.session_token,
            'description': description,
            'success_redirect_url': reverse(
                'gocardless-redirectflow-success',
            )
        }

        return super(RedirectFlow, cls).create(
            params,
            redirectflow,
            *args,
            **kwargs
        )

    def complete(self, *args, **kwargs):
        resource = self.from_api(
            self.api.complete,
            self.id,
            params={
                'session_token': self.session_token
            }
        )
        self.from_resource(resource)
        self.save(*args, **kwargs)

    def __str__(self):
        return self.id


class Payout(models.Model, GCCacheMixin):

    """
    Payouts represent transfers from GoCardless to a creditor. Each payout
    contains the funds collected from one or many payments. Payouts are created
    automatically after a payment has been successfully collected.
    """

    id = models.CharField(
        primary_key=True,
        max_length=255
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True
    )
    created_at = models.DateTimeField(
        null=True
    )
    currency = models.CharField(
        max_length=3,
        blank=True,
        choices=CURRENCIES
    )
    reference = models.CharField(
        max_length=140,
        blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=PAYOUT_STATUSES,
        default=PAYOUT_STATUSES[0][0]
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.id

    @staticmethod
    def paid(sender, payout, event, merchant=None, **kwargs):
        payout.status = PAYOUT_STATUSES[1][0]
        payout.save()


class Subscription(models.Model, GCCreateUpdateMixin):

    """
    Subscriptions create payments according to a schedule.
    """

    create_fields = {
        'required': [
            'amount',
            'currency',
            'interval_unit',
            {
                'links': [
                    'mandate'
                ]
            }
        ],
        'optional': [
            'count',
            'day_of_month',
            'end_date',
            'interval',
            'month',
            'name',
            'payment_reference',
            'start_date',
        ]
    }

    update_fields = {
        'optional': [
            'name',
            'payment_reference',
        ],
    }

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
    created_at = models.DateTimeField(
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
        Mandate,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name if self.name else self.id

    @cached_property
    def merchant(self):
        try:
            return self.mandate.merchant
        except ObjectDoesNotExist:
            return None

    @property
    def upcoming_payments(self):
        raise NotImplementedError('Upcoming payments are not yet implemented.')

    @classmethod
    def create(cls, given, *args, **kwargs):
        cls.validate_fields(
            cls.create_fields,
            given
        )

        mandate = model_from_links(
            given['links'],
            'mandate'
        )
        instance = cls(
            mandate=mandate
        )

        return super(Subscription, cls).create(
            given,
            instance=instance,
            check=False,
            *args,
            **kwargs
        )

    @staticmethod
    def created(sender, subscription, event, merchant=None, **kwargs):
        subscription.fetch(subscription)

    @staticmethod
    def payment_created(sender, subscription, event, merchant=None, **kwargs):
        subscription.fetch(subscription)

    @staticmethod
    def cancelled(sender, subscription, event, merchant=None, **kwargs):
        subscription.status = SUBSCRIPTION_STATUSES[4][0]


class Payment(models.Model, GCCreateMixin):

    """
    Payment objects represent payments from a customer to a creditor, taken
    against a Direct Debit mandate.
    """

    create_fields = {
        'required': [
            'amount',
            'currency',
            {
                'links': [
                    'mandate',
                ],
            },
        ],
        'optional': [
            'app_fee',
            'charge_date',
            'description',
            'reference',
        ]
    }
    client_source_create = 'mandate'

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
    created_at = models.DateTimeField(
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
        on_delete=models.CASCADE,
        null=True
    )
    payout = models.ForeignKey(
        Payout,
        on_delete=models.CASCADE,
        null=True
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.id

    @cached_property
    def merchant(self):
        return self.mandate.merchant if self.mandate is not None else None

    @staticmethod
    def created(sender, payment, event, merchant=None, **kwargs):
        payment.fetch(payment)

    @staticmethod
    def submitted(sender, payment, event, merchant=None, **kwargs):
        payment.status = PAYMENT_STATUSES[1][0]
        payment.save()

    @staticmethod
    def confirmed(sender, payment, event, merchant=None, **kwargs):
        payment.status = PAYMENT_STATUSES[2][0]
        payment.save()

    @staticmethod
    def cancelled(sender, payment, event, merchant=None, **kwargs):
        payment.status = PAYMENT_STATUSES[6][0]
        payment.save()

    @staticmethod
    def failed(sender, payment, event, merchant=None, **kwargs):
        payment.status = PAYMENT_STATUSES[3][0]
        payment.save()

    @staticmethod
    def charged_back(sender, payment, event, merchant=None, **kwargs):
        payment.status = PAYMENT_STATUSES[4][0]
        payment.save()

    @staticmethod
    def chargeback_cancelled(sender, payment, event, merchant=None, **kwargs):
        payment.fetch(payment)

    @staticmethod
    def paid_out(sender, payment, event, merchant=None, **kwargs):
        payment.fetch(payment)

    @staticmethod
    def late_failure_settled(sender, payment, event, merchant=None, **kwargs):
        payment.failed(payment, event)

    @staticmethod
    def chargeback_settled(sender, payment, event, merchant=None, **kwargs):
        payment.charged_back(payment, event)

    @staticmethod
    def resubmission_requested(sender, payment, event, merchant=None, **kwargs):
        payment.submitted(payment, event)


class Refund(models.Model, GCCacheMixin):

    """
    Refund objects represent (partial) refunds of a payment back to the
    customer.
    """

    id = models.CharField(
        primary_key=True,
        max_length=255
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True
    )
    created_at = models.DateTimeField(
        null=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES,
        blank=True
    )
    reference = models.CharField(
        max_length=140,
        blank=True
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.id

    @cached_property
    def merchant(self):
        return self.payment.merchant if self.payment is not None else None

    @staticmethod
    def created(sender, refund, event, merchant=None, **kwargs):
        refund.fetch(refund)

    @staticmethod
    def paid(sender, refund, event, merchant=None, **kwargs):
        pass

    @staticmethod
    def settled(sender, refund, event, merchant=None, **kwargs):
        pass
