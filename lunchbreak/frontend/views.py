from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from lunch.models import Store

from .forms import SearchForm


@method_decorator(csrf_exempt, name='dispatch')
class IndexView(SearchForm.ViewMixin, TemplateView):
    template_name = 'pages/index.html'


@method_decorator(csrf_exempt, name='dispatch')
class SearchView(SearchForm.ViewMixin, TemplateView):
    template_name = 'pages/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = context['search_form']
        if search_form.is_valid():
            stores = Store.objects.nearby(
                latitude=search_form.latitude,
                longitude=search_form.longitude,
                proximity=10
            )

            for store in stores:
                if store.distance < 1:
                    store.distance = '{distance} m'.format(
                        distance=int(store.distance * 1000)
                    )
                else:
                    store.distance = '{0:.2f} km'.format(
                        store.distance
                    ).replace('.', ',')
        else:
            stores = Store.objects.all().annotate(
                hearts_count=Count('hearts')
            ).order_by(
                '-hearts_count'
            )
        context['stores'] = stores
        return context


class StoreView(TemplateView):
    template_name = 'pages/store.html'

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = Store.objects.select_related(
            'header',
        ).prefetch_related(
            'categories',
            'regions',
            'menus__food',
        ).get(
            pk=pk
        )
        return context
