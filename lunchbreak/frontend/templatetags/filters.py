import json
from datetime import date, datetime

from django.conf import settings
from django.template.defaultfilters import date as date_filter
from django.template.defaultfilters import time as time_filter
from django.utils.translation import ugettext_lazy as _
from django_jinja import library
from jinja2 import Markup
from lunch.config import INPUT_SI_VARIABLE, WEEKDAYS
from pendulum import Pendulum


@library.filter
def list_periods(periods, arg='H:i'):
    """
    Usage: {{ 'Hello'|mylower() }}
    """
    return ', '.join([
        '{start} - {end}'.format(
            start=time_filter(period.start.time(), arg),
            end=time_filter(period.end.time(), arg)
        ) for period in periods
    ])


@library.filter
def json_weekday_periods(weekday_periods, **kwargs):
    """
    Usage: {{ 'Hello'|mylower() }}
    """
    result = {}
    for weekday, periods in weekday_periods.items():
        result[weekday] = list_periods(
            periods=periods,
            **kwargs
        )
    return json.dumps(result)


@library.filter
def humanize_weekday(value):
    if hasattr(value, 'isoweekday'):
        value = value.isoweekday()

    today = Pendulum.today(settings.TIME_ZONE)
    if value == today.isoweekday():
        return _('Vandaag')
    elif value == Pendulum.tomorrow(settings.TIME_ZONE).isoweekday():
        return _('Morgen')
    elif value == today.add(days=2).isoweekday():
        return _('Overmorgen')
    elif value == today.subtract(days=1).isoweekday():
        return _('Gisteren')
    elif value == today.subtract(days=2).isoweekday():
        return _('Eergisteren')

    for weekday in WEEKDAYS:
        number = weekday[0]

        if number == value:
            return weekday[1]

    return ''


@library.filter
def humanize_date(value, arg='j F Y'):
    if isinstance(value, datetime):
        value = Pendulum.instance(value)
    elif isinstance(value, date):
        value = Pendulum.create_from_date(
            year=value.year,
            month=value.month,
            day=value.day
        )

    result = humanize_weekday(value)
    if abs(Pendulum.now().diff(value).in_days()) > 2:
        result += ' ' + date_filter(value, arg)
    return result


@library.filter
def money(value):
    """Format money in the correct format."""
    return Markup(
        '{symbol}&euro; {value:.2f}'.format(
            symbol='- ' if value < 0 else '',
            value=abs(value),
        ).replace('.', ',')
    )


@library.filter
def percentage(value):
    """Format percentage in the correct format."""
    return '{value}%'.format(
        value=str(value).replace('.', ',').rstrip(',0')
    )


@library.filter
def amount(value, inputtype):
    """Get the amount formatted in a correct format."""
    if inputtype == INPUT_SI_VARIABLE:
        if value < 1:
            return '{value} g'.format(
                value=int(value * 1000)
            )
        else:
            return '{value} kg'.format(
                value=str(value.normalize()).replace('.', ',')
            )
    else:
        return int(value)
