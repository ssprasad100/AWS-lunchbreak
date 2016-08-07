from django import forms
from lunch.models import AbstractAddress


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
                address = form.data['address']
                form.latitude, form.longitude = AbstractAddress.geocode(
                    address=address
                )
            context['search_form'] = form
            return context
