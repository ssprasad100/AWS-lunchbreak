import json

from customers.config import PAYMENT_METHODS
from customers.models import Group, GroupOrder, Order, User
from django import forms
from django.utils.translation import ugettext as _
from lunch.exceptions import AddressNotFound
from lunch.models import AbstractAddress
from Lunchbreak.forms import FatModelForm

from .widgets import DayWidget, ReceiptWidget


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
            store=self.store
        )

        description = self.fields['description']
        description.widget.attrs['placeholder'] = description.help_text

        group_field = self.fields['group']
        group_field.queryset = self.user.store_groups.filter(
            store_id=self.store.id
        )
        if len(group_field.queryset) > 0:
            group_field.initial = group_field.queryset[0]
        group_field.groups_json = json.dumps(
            {
                group.id: {
                    'deadline': group.deadline.strftime('%H:%M'),
                    'receipt': group.receipt.strftime('%H:%M'),
                    'delivery': group.delivery
                } for group in group_field.queryset
            }
        )
        group_field.label = Group._meta.verbose_name.capitalize()
        group_field.widget.attrs['class'] = 'input-icon icon-dropdown input-icon-right'

    def create_instance(self, **kwargs):
        return Order.objects.create_with_orderedfood(
            orderedfood=None,
            save=False,
            **kwargs
        )

    def save(self, temporary_order):
        return temporary_order.place(
            **self.cleaned_data
        )


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
            orders__isnull=False
        ).distinct().values(
            'date'
        )
        group_order_days = [group_order['date'] for group_order in group_orders]

        self.fields['day'].widget = DayWidget(
            days=group_order_days
        )

    @property
    def group_order(self):
        return GroupOrder.objects.filter(
            group=self.group,
            date=self['day'].value()
        ).first()
