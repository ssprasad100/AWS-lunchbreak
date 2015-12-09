import django.dispatch

mandate_created = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_submitted = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_active = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_reinstated = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_transferred = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_cancelled = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_failed = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_expired = django.dispatch.Signal(
    providing_args=['mandate']
)
mandate_resubmission_requested = django.dispatch.Signal(
    providing_args=['mandate']
)
