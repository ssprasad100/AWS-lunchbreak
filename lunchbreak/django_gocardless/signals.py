from django.dispatch import Signal

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

payout_paid = Signal(
    providing_args=[
        'payout',
        'event',
        'merchant',
    ]
)

refund_created = Signal(
    providing_args=[
        'refund',
        'event',
        'merchant',
    ]
)
refund_paid = Signal(
    providing_args=[
        'refund',
        'event',
        'merchant',
    ]
)
refund_settled = Signal(
    providing_args=[
        'refund',
        'event',
        'merchant',
    ]
)
