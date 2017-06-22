import json

from customers.config import ORDER_STATUSES_ENDED
from customers.models import (ConfirmedOrder, Group, Order, PaymentLink,
                              TemporaryOrder)
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from django.views.generic.base import RedirectView
from lunch.models import Food, Store
from payconiq import get_widget_url
from user_agents import parse as parse_user_agent

from .forms import GroupForm, OrderForm, SearchForm, UserForm
from .mixins import LoginForwardMixin
from .utils import add_query_params


@method_decorator(csrf_exempt, name='dispatch')
class IndexView(SearchForm.ViewMixin, TemplateView):
    template_name = 'pages/index.html'


@method_decorator(csrf_exempt, name='dispatch')
class SearchView(SearchForm.ViewMixin, TemplateView):
    template_name = 'pages/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = context['search_form']
        stores = []

        if search_form.is_valid():
            stores_byname = Store.objects.filter(
                name__icontains=search_form.data['address'],
                enabled=True
            )
            stores = list(stores_byname)

            if hasattr(search_form, 'latitude'):
                stores_nearby = Store.objects.nearby(
                    latitude=search_form.latitude,
                    longitude=search_form.longitude,
                    proximity=10
                )

                stores += list(stores_nearby)

            for store in stores:
                if not hasattr(store, 'distance'):
                    continue

                if store.distance < 1:
                    store.distance = '{distance} m'.format(
                        distance=int(store.distance * 1000)
                    )
                else:
                    store.distance = '{0:.2f} km'.format(
                        store.distance
                    ).replace('.', ',')

        if not stores:
            stores = Store.objects.filter(
                enabled=True
            ).annotate(
                hearts_count=Count('hearts')
            ).order_by(
                '-hearts_count'
            )
            context['popular_stores'] = True
        context['stores'] = stores
        return context


class StoreView(TemplateView):
    template_name = 'pages/store.html'

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = get_object_or_404(
            Store.objects.select_related(
                'header',
            ).prefetch_related(
                'categories',
                'regions',
                'menus__food',
            ),
            pk=pk,
            enabled=True
        )
        return context


class OrderView(LoginForwardMixin, TemplateView):
    template_name = 'pages/order.html'
    forward_group = 'frontend-order'

    @property
    def data(self):
        return getattr(
            self.request,
            'forward_data',
            self.request.POST
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.data
        context['store'] = get_object_or_404(
            Store,
            pk=kwargs['store_id'],
            enabled=True
        )

        if 'orderedfood' in data:
            orderedfoods_list = [json.loads(d) for d in data.getlist('orderedfood')]
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
                return context

        # Only validate the form if it's a post request
        form_data = data if self.request.method == 'POST' and 'orderedfood' not in data else None

        context['user_form'] = UserForm(
            data=form_data,
            instance=self.request.user
        )
        context['order_form'] = OrderForm(
            data=form_data,
            store=context['store'],
            user=self.request.user,
            temporary_order=context['order']
        )

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'order' not in context:
            return HttpResponseRedirect(
                reverse(
                    'frontend:store',
                    kwargs={
                        'pk': kwargs['store_id']
                    }
                )
            )

        user_form = context['user_form']
        order_form = context['order_form']
        if request.method == 'POST' and user_form.is_valid() and order_form.is_valid():
            user_form.save()

            if order_form.needs_paymentlink:
                store = context['store']
                paymentlink = PaymentLink.create(
                    user=self.request.user,
                    store=store,
                    completion_redirect_url=request.build_absolute_uri(
                        reverse(
                            'frontend:order',
                            kwargs={
                                'store_id': store.id
                            }
                        )
                    )
                )
                response = self.create_forward(
                    request=request,
                    data=self.data,
                    response=redirect(
                        to=paymentlink.redirectflow.redirect_url
                    )
                )
                return response

            placed_order = order_form.save(
                temporary_order=context['order']
            )

            if placed_order.payment_payconiq:
                return HttpResponseRedirect(
                    reverse(
                        'frontend:payconiq',
                        kwargs={
                            'store_id': placed_order.store_id,
                            'order_id': placed_order.id
                        }
                    )
                )
            return HttpResponseRedirect(
                reverse(
                    'frontend:confirm',
                    kwargs={
                        'store_id': placed_order.store_id,
                        'order_id': placed_order.id
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.request.GET.get('group')
        context['group'] = Group.objects.filter(
            pk=group_id
        ).first()
        return context

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


class ConfirmView(TemplateView):
    template_name = 'pages/confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['store'] = Store.objects.get(
                id=kwargs['store_id'],
                enabled=True
            )
            context['order'] = ConfirmedOrder.objects.get(
                id=kwargs['order_id']
            )
        except (Store.DoesNotExist, Order.DoesNotExist):
            raise Http404()

        if context['order'].user != self.request.user \
                or context['order'].status in ORDER_STATUSES_ENDED:
            raise Http404()

        return context

    def get(self, request, store_id, order_id):
        context = self.get_context_data(
            store_id=store_id,
            order_id=order_id
        )

        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )


class PayconiqView(TemplateView):
    template_name = 'pages/payconiq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['store'] = Store.objects.get(
                id=kwargs['store_id'],
                enabled=True
            )
            context['order'] = Order.objects.select_related(
                'transaction'
            ).get(
                id=kwargs['order_id']
            )
        except (Store.DoesNotExist, Order.DoesNotExist):
            raise Http404()

        if context['order'].user != self.request.user \
                or context['order'].status in ORDER_STATUSES_ENDED \
                or not context['order'].payment_payconiq:
            raise Http404()

        context['payconiq_widget_url'] = get_widget_url()

        return context

    def get(self, request, store_id, order_id):
        context = self.get_context_data(
            store_id=store_id,
            order_id=order_id
        )

        if context['order'].confirmed:
            return HttpResponseRedirect(
                reverse(
                    'frontend:confirm',
                    kwargs={
                        'store_id': self.kwargs['store_id'],
                        'order_id': self.kwargs['order_id']
                    }
                )
            )

        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(
            reverse('frontend:index')
        )


class TermsView(TemplateView):
    template_name = 'pages/terms.html'


class GroupView(TemplateView):
    template_name = 'pages/group.html'
    login_url = reverse_lazy('frontend:login')

    def get_context_data(self, request, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(
            Group.objects.prefetch_related(
                'members'
            ),
            pk=pk
        )
        context['title'] = _('Lunchbreak: Groep %(group_name)s') % {
            'group_name': context['group'].name
        }
        context['group_form'] = GroupForm(
            data=request.GET,
            group=context['group']
        )
        return context

    def get(self, request, pk, **kwargs):
        context = self.get_context_data(request, pk, **kwargs)
        group = context['group']
        token = request.GET.get('token')

        if token is None or group.admin_token != token:
            raise Http404()

        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )


class GroupJoinView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/group-join.html'

    @property
    def login_url(self):
        login_url = reverse('frontend:login')
        return add_query_params(url=login_url, group=self.group.id)

    @property
    def group(self):
        if not hasattr(self, '_group'):
            self._group = get_object_or_404(
                Group,
                pk=self.kwargs['pk'],
                join_token=self.request.GET.get('token')
            )
        return self._group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_member = self.group.members.filter(
            pk=self.request.user.pk
        ).exists()
        if not is_member:
            self.group.members.add(self.request.user)
        context['group'] = self.group
        context['title'] = _('Lunchbreak: Groep %(group_name)s') % {
            'group_name': self.group.name
        }
        return context


class AndroidView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return 'https://play.google.com/store/apps/details?id=be.lunchbreakapp.lunchbreak'


class IOSView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return 'https://itunes.apple.com/app/id949238693'
