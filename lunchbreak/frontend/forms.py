from customers.config import PAYMENT_METHOD_GOCARDLESS, PAYMENT_METHODS
from customers.models import Order, User
from django import forms
from lunch.exceptions import AddressNotFound
from lunch.models import AbstractAddress
from Lunchbreak.forms import FatModelForm

from .widgets import ReceiptField


class SearchForm(forms.Form):
    address = forms.CharField(
        required=True,
        help_text='Vul je adres in',
        error_messages={
            'required': 'Vul je adres in om winkels in de buurt te zoeken.',
            'invalid': 'Kon je plaats niet bepalen, probeer opnieuw.'
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
        for field_name in ['name', 'email']:
            self.fields[field_name].required = True
            self.fields[field_name].widget.attrs['placeholder'] = self.fields[field_name].label


class OrderForm(FatModelForm):

    class Meta:
        model = Order
        fields = ['payment_method', 'receipt', 'description']

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
        self.fields['receipt'].widget = ReceiptField(
            store=self.store
        )

        description = self.fields['description']
        description.widget.attrs['placeholder'] = description.help_text

    def save(self, temporary_order):
        return temporary_order.place(
            **self.cleaned_data
        )

    @property
    def needs_paymentlink(self):
        try:
            is_gocardless = int(self['payment_method'].value()) == PAYMENT_METHOD_GOCARDLESS
            return is_gocardless and 'payment_method' in self.errors.as_data()
        except (ValueError, TypeError):
            return False
