from django.dispatch import Signal

from .models import (CustomerBankAccount, Mandate, Merchant, Payment,
                     Subscription)

LINK_MODELS = {
    'mandate': Mandate,
    'previous_customer_bank_account': CustomerBankAccount,
    'new_customer_bank_account': CustomerBankAccount,
    'organisation': {
        'model': Merchant,
        'id_field': 'organisation_id',
        'argument': 'organisation',
    },
    'payment': Payment,
    'subscription': Subscription
}

mandate_created = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_submitted = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_active = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_reinstated = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_transferred = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
        'previous_customer_bank_account',
        'new_customer_bank_account',
    ]
)
mandate_cancelled = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_failed = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_expired = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)
mandate_resubmission_requested = Signal(
    providing_args=[
        'mandate',
        'event',
        'merchant',
    ]
)

payment_created = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_submitted = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_confirmed = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_cancelled = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_failed = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_charged_back = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_chargeback_cancelled = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_paid_out = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_late_failure_settled = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_chargeback_settled = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)
payment_resubmission_requested = Signal(
    providing_args=[
        'payment',
        'event',
        'merchant',
    ]
)

subscription_created = Signal(
    providing_args=[
        'subscription',
        'event',
        'merchant',
    ]
)
subscription_payment_created = Signal(
    providing_args=[
        'subscription',
        'event',
        'merchant',
    ]
)
subscription_cancelled = Signal(
    providing_args=[
        'subscription',
        'event',
        'merchant',
    ]
)
