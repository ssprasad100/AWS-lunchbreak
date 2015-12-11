import django.dispatch

from .models import CustomerBankAccount, Mandate, Merchant

LINK_MODELS = {
    'mandate': Mandate,
    'previous_customer_bank_account': CustomerBankAccount,
    'new_customer_bank_account': CustomerBankAccount,
    'organisation': {
        'model': Merchant,
        'where_field': 'organisation_id',
        'argument': 'organisation',
    }
}

mandate_created = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_submitted = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_active = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_reinstated = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_transferred = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
        'previous_customer_bank_account',
        'new_customer_bank_account',
    ]
)
mandate_cancelled = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_failed = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_expired = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_resubmission_requested = django.dispatch.Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
