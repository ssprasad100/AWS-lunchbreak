from django.dispatch import Signal

transaction_timedout = Signal(
    providing_args=[
        'transaction',
    ]
)
transaction_canceled = Signal(
    providing_args=[
        'transaction',
    ]
)
transaction_failed = Signal(
    providing_args=[
        'transaction',
    ]
)
transaction_succeeded = Signal(
    providing_args=[
        'transaction',
    ]
)
