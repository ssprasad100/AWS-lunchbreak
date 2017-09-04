from datetime import datetime

from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from lunch.models import Period
from pendulum import Pendulum


class ReceiptWidget(widgets.Widget):

    supports_microseconds = False
    name_weekday = '-weekday'
    name_time = '-time'

    def __init__(self, store, orderedfood, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store
        self.orderedfood = orderedfood

    def render(self, name, value, attrs=None):
        return mark_safe(
            render_to_string(
                template_name='widgets/receipt_field.html',
                context={
                    'name_weekday': name + self.name_weekday,
                    'name_time': name + self.name_time,
                    'value': value,
                    'attrs': attrs,
                    'store': self.store,
                    'orderedfood': self.orderedfood,
                }
            )
        )

    def value_from_datadict(self, data, files, name):
        try:
            time = datetime.strptime(
                data.get(name + self.name_time),
                '%H:%M'
            ).time()
            return Period.weekday_as_datetime(
                weekday=int(data.get(name + self.name_weekday)),
                time=time,
                store=self.store
            )._datetime
        except (TypeError, ValueError):
            return None


class DayWidget(widgets.Widget):

    supports_microseconds = False
    query_param = 'day'

    def __init__(self, group, days, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.days = days

    def render(self, name, value, attrs=None):
        return mark_safe(
            render_to_string(
                template_name='widgets/day_field.html',
                context={
                    'days': self.days,
                    'query_param': self.query_param,
                    'value': value,
                    'group': self.group,
                }
            )
        )

    def value_from_datadict(self, data, files, name):
        try:
            result = Pendulum.parse(
                data.get(self.query_param)
            ).date()
            if result in self.days:
                return result
        except (ValueError, OverflowError):
            pass
        now = Pendulum.now()
        try:
            return min(
                self.days,
                key=lambda date: now.diff(
                    Pendulum.create(
                        year=date.year,
                        month=date.month,
                        day=date.day
                    )
                )
            )
        # Thrown if self.days is empty
        except ValueError:
            return None
