import json
from datetime import date, datetime
from decimal import Decimal

from django.conf import settings
from django.template.defaultfilters import date as date_filter
from django.template.defaultfilters import time as time_filter
from django.utils.translation import ugettext_lazy as _
from django_jinja import library
from jinja2 import Markup
from lunch.config import INPUT_SI_VARIABLE, WEEKDAYS
from pendulum import Pendulum

from ..utils import add_query_params


@library.filter
def absolute_url(path, **params):
    """Usage: {{ url('view-name') | absolute_url }}

    Additional params will be url encoded.
    """
    url = '{protocol}://{domain}{path}'.format(
        protocol='https' if settings.SSL else 'http',
        domain=settings.ALLOWED_HOSTS[0],
        path=path
    )
    return add_query_params(url=url, **params)


@library.filter
def list_periods(periods, arg='H:i'):
    return ', '.join([
        '{start} - {end}'.format(
            start=time_filter(period.start.time(), arg),
            end=time_filter(period.end.time(), arg)
        ) for period in periods
    ])


@library.filter
def json_weekday_periods(weekday_periods, **kwargs):
    result = {}
    for weekday, periods in weekday_periods.items():
        result[weekday] = list_periods(
            periods=periods,
            **kwargs
        )
    return json.dumps(result)


@library.filter
def naturalweekday(value):
    today = Pendulum.today(settings.TIME_ZONE)

    if isinstance(value, int):
        value = today.subtract(
            days=today.isoweekday()
        ).add(
            days=value
        )

    if not isinstance(value, date):
        value = value.date()

    if value == today.date():
        return _('Vandaag')
    elif value == Pendulum.tomorrow(settings.TIME_ZONE).date():
        return _('Morgen')
    elif value == today.add(days=2).date():
        return _('Overmorgen')
    elif value == today.subtract(days=1).date():
        return _('Gisteren')
    elif value == today.subtract(days=2).date():
        return _('Eergisteren')

    value_weekday = value.isoweekday()
    for weekday in WEEKDAYS:
        number = weekday[0]

        if number == value_weekday:
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

    result = naturalweekday(value)
    if abs(Pendulum.now().diff(value).in_days()) > 2:
        result += ' ' + date_filter(value, arg)
    return result


@library.filter
def money(value):
    """Format money in the correct format."""
    return Markup(
        '{symbol}&euro; {value:.2f}'.format(
            symbol='- ' if value < 0 else '',
            value=abs(
                (
                    Decimal(value) / Decimal(100)
                ).quantize(
                    Decimal('0.01')
                )
            ),
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
