import django.dispatch

mandate_created = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_submitted = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_active = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_reinstated = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_transferred = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_cancelled = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_failed = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_expired = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
mandate_resubmission_requested = django.dispatch.Signal(
    providing_args=['instance', 'event']
)
