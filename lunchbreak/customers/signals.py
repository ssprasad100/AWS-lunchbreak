from django.dispatch import Signal

order_created = Signal(
    providing_args=[
        'order',
    ]
)
order_denied = Signal(
    providing_args=[
        'order',
    ]
)
order_received = Signal(
    providing_args=[
        'order',
    ]
)
order_started = Signal(
    providing_args=[
        'order',
    ]
)
order_waiting = Signal(
    providing_args=[
        'order',
    ]
)
order_completed = Signal(
    providing_args=[
        'order',
    ]
)
order_not_collected = Signal(
    providing_args=[
        'order',
    ]
)

group_order_created = Signal(
    providing_args=[
        'group_order',
    ]
)
