import json

from customers.models import TemporaryOrder
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from lunch.models import Food, Store
from user_agents import parse as parse_user_agent

from .forms import SearchForm
from .mixins import LoginForwardMixin


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


class OrderView(LoginForwardMixin, TemplateView):
    template_name = 'pages/order.html'
    forward_group = 'frontend-order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = getattr(
            self.request,
            'forward_data',
            dict(self.request.POST)
        )

        context['store'] = get_object_or_404(
            Store,
            pk=kwargs['store_id']
        )
        if 'orderedfood' in data:
            orderedfoods_list = [json.loads(d) for d in data['orderedfood']]
            for orderedfood in orderedfoods_list:
                orderedfood['original'] = Food.objects.get(
                    pk=orderedfood['original']
                )

            context['order'] = TemporaryOrder.objects.create_with_orderedfood(
                orderedfood=orderedfoods_list,
                store=context['store'],
                user=self.request.user
            )
        else:
            try:
                context['order'] = TemporaryOrder.objects.get(
                    store=context['store'],
                    user=self.request.user
                )
            except TemporaryOrder.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'order' not in context:
            return HttpResponseRedirect(
                reverse(
                    'frontend-store',
                    kwargs={
                        'pk': kwargs['store_id']
                    }
                )
            )
        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )


class LoginView(TemplateView):
    template_name = 'pages/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(
                request.GET.get('next', settings.LOGIN_REDIRECT_URL)
            )
        response = super().dispatch(request, *args, **kwargs)

        user_agent_meta = request.META.get('HTTP_USER_AGENT', None)
        if user_agent_meta is not None:
            user_agent = parse_user_agent(user_agent_meta)
            device = '{device} {os} {browser}'.format(
                device=user_agent.device.family,
                os=user_agent.os.family,
                browser=user_agent.browser.family
            ).strip()
        else:
            device = 'Onbekend toestel'

        response.set_cookie(
            'device',
            device
        )

        return response

    def post(self, request, *args, **kwargs):
        phone = request.POST.get('login-phone')
        identifier = request.POST.get('login-identifier')
        device = request.COOKIES.get('device')

        user = authenticate(
            identifier=identifier,
            device=device,
            phone=phone
        )

        if user is None:
            return self.get(request, *args, **kwargs)

        login(request, user)
        return HttpResponseRedirect(
            request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        )


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(
            reverse('frontend-index')
        )
