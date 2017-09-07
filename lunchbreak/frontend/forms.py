import json

from customers.config import (ORDER_STATUS_COMPLETED,
                              ORDER_STATUS_NOT_COLLECTED, ORDER_STATUS_PLACED,
                              ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                              ORDER_STATUS_WAITING, PAYMENT_METHOD_CASH,
                              PAYMENT_METHOD_GOCARDLESS,
                              PAYMENT_METHOD_PAYCONIQ, PAYMENT_METHODS)
from customers.models import Group, GroupOrder, Order, User
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext as _
from lunch.exceptions import AddressNotFound
from lunch.models import AbstractAddress
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.forms import FatModelForm
from payconiq.models import Transaction

from .widgets import DayWidget, ReceiptWidget


class CancelTransaction(Exception):
    pass


class SearchForm(forms.Form):
    address = forms.CharField(
        required=True,
        help_text=_('Vul je adres in'),
        error_messages={
            'required': _('Vul je adres in om winkels in de buurt te zoeken.'),
            'invalid': _('Kon je plaats niet bepalen, probeer opnieuw.')
        }
    )

    class ViewMixin:

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            form = SearchForm(self.request.GET)
            if form.is_valid():
                try:
                    form.latitude, form.longitude = AbstractAddress.geocode(
                        address=form.data['address']
                    )
                except AddressNotFound:
                    pass
            context['search_form'] = form
            return context


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True

        for field_name in ['name', 'email']:
            self.fields[field_name].widget.attrs['placeholder'] = self.fields[field_name].label


class OrderForm(FatModelForm):
    group = forms.ModelChoiceField(
        required=False,
        queryset=Group.objects.none(),
        empty_label=_('Privé bestellen'),
        error_messages={
            'invalid_choice': _('%(value)s is geen geldige keuze.')
        }
    )

    class Meta:
        model = Order
        fields = ['payment_method', 'receipt', 'description', 'group', ]

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop('store')
        self.user = kwargs.pop('user')
        self.temporary_order = kwargs.pop('temporary_order')
        super().__init__(*args, **kwargs)

        self.instance_data = {
            'store': self.store,
            'user': self.user
        }

        self.fields['payment_method'].required = True
        self.fields['payment_method'].widget = forms.widgets.RadioSelect(
            choices=PAYMENT_METHODS
        )
        self.fields['receipt'].required = True
        self.fields['receipt'].widget = ReceiptWidget(
            store=self.store,
            orderedfood=self.temporary_order.orderedfood.select_related(
                'original',
            ).all()
        )

        description = self.fields['description']
        description.widget.attrs['placeholder'] = description.help_text

        group_field = self.fields['group']
        user_groups = self.user.store_groups.filter(
            store_id=self.store.id
        )
        group_field.queryset = user_groups
        if len(group_field.queryset) > 0:
            group_field.initial = group_field.queryset[0]
        group_field.groups_json = json.dumps(
            {
                group.id: {
                    'deadline': group.deadline.strftime('%H:%M'),
                    'receipt': group.receipt_time.strftime('%H:%M'),
                    'delivery': group.delivery
                } for group in group_field.queryset
            }
        )
        group_field.label = Group._meta.verbose_name.capitalize()
        group_field.widget.attrs['class'] = 'input-icon icon-dropdown input-icon-right'

    def create_instance(self, **kwargs):
        try:
            with transaction.atomic():
                order = self.temporary_order.place(
                    create_transaction=False,
                    **self.cleaned_data
                )
                raise CancelTransaction()
        except CancelTransaction:
            return order
        except ValidationError as e:
            self.add_error(
                'receipt',
                e
            )
        except LunchbreakException as e:
            self.add_error(
                'receipt',
                e.detail
            )

    def save(self, temporary_order):
        return temporary_order.place(
            create_transaction=False,
            **self.cleaned_data
        )

    @property
    def needs_paymentlink(self):
        try:
            is_gocardless = int(self['payment_method'].value()) == PAYMENT_METHOD_GOCARDLESS
            return is_gocardless and 'payment_method' in self.errors.as_data()
        except (ValueError, TypeError):
            return False


class GroupForm(forms.ModelForm):
    day = forms.DateField(
        required=True
    )

    class Meta:
        model = Group
        fields = ('day',)

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        super().__init__(*args, **kwargs)

        group_orders = self.group.group_orders.filter(
            Q(
                orders__isnull=False,
                orders__status__in=[
                    ORDER_STATUS_PLACED,
                    ORDER_STATUS_RECEIVED,
                    ORDER_STATUS_STARTED,
                    ORDER_STATUS_WAITING,
                    ORDER_STATUS_COMPLETED,
                    ORDER_STATUS_NOT_COLLECTED,
                ]
            ) & (
                Q(
                    orders__payment_method__in=[PAYMENT_METHOD_CASH, PAYMENT_METHOD_GOCARDLESS],
                ) | Q(
                    orders__payment_method=PAYMENT_METHOD_PAYCONIQ,
                    orders__transaction__isnull=False,
                    orders__transaction__status=Transaction.SUCCEEDED,
                )
            )
        ).order_by(
            '-date'
        ).distinct().values(
            'date'
        )
        group_order_days = [group_order['date'] for group_order in group_orders]

        self.fields['day'].widget = DayWidget(
            group=self.group,
            days=group_order_days,
        )

    @property
    def group_order(self):
        return GroupOrder.objects.filter(
            group=self.group,
            date=self['day'].value()
        ).first()
