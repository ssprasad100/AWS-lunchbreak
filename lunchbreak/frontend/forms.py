from django import forms


class SearchForm(forms.Form):
    location = forms.CharField(help_text='Vul je adres in')

    class ViewMixin:

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['search_form'] = SearchForm()
            return context
