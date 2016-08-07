from django.views.generic import TemplateView

from .forms import SearchForm


class IndexView(SearchForm.ViewMixin, TemplateView):
    template_name = 'pages/index.html'


class SearchView(SearchForm.ViewMixin, TemplateView):
    template_name = 'pages/search.html'
