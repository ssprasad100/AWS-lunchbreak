from django.template.defaultfilters import time
from django_jinja import library
from lunch.config import WEEKDAYS


@library.filter
def list_periods(periods, arg='H:i'):
    """
    Usage: {{ 'Hello'|mylower() }}
    """
    return ', '.join([
        '{start} - {end}'.format(
            start=time(period.start.time(), arg),
            end=time(period.end.time(), arg)
        ) for period in periods
    ])


@library.filter
def humanize_weekday(value):
    for weekday in WEEKDAYS:
        number = weekday[0]

        if number == value:
            return weekday[1]

    return ''
