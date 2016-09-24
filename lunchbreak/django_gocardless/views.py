import hashlib
import hmac
import json
from urllib.parse import urlencode

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView, View
from gocardless_pro.resources import Event

from .exceptions import (BadRequestError, ExchangeAuthorisationError,
                         RedirectFlowAlreadyCompletedError,
                         RedirectFlowIncompleteError)
from .handlers import EventHandler
from .models import Merchant, RedirectFlow


class RedirectFlowCreateView(RedirectView):

    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        redirectflow = RedirectFlow.create()
        return redirectflow.redirect_url


class RedirectFlowSuccessView(View):

    def get(self, request, *args, **kwargs):
        redirectflow_id = request.GET.get('redirect_flow_id', None)

        response = HttpResponse(
            status=307,  # Temporary redirect
        )
        response['Location'] = settings.GOCARDLESS['redirectflow']
        if redirectflow_id is not None:
            try:
                redirectflow = RedirectFlow.objects.get(
                    id=redirectflow_id
                )
                params = {}
                redirectflow.complete()
            except RedirectFlow.DoesNotExist:
                raise Http404('RedirectFlow not found.')
            except RedirectFlowIncompleteError:
                params['error'] = 'incomplete'
            except RedirectFlowAlreadyCompletedError:
                params['error'] = 'completed'
            except BadRequestError:
                params['error'] = 'invalid'
            except:
                params['error'] = 'default'

        url = redirectflow.completion_redirect_url

        if params:
            data = urlencode(params)
            url += '?' + data

        response['Location'] = url

        return response


class CSRFExemptView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class WebhookView(CSRFExemptView):

    INVALID_TOKEN = 498

    def post(self, request, *args, **kwargs):
        webhook_signature = request.META.get('HTTP_WEBHOOK_SIGNATURE', None)

        if webhook_signature is None:
            return HttpResponse(
                status=self.INVALID_TOKEN
            )

        is_app = kwargs.get('is_app', False)
        secret = secret = settings.GOCARDLESS['app']['webhook']['secret'] \
            if is_app else settings.GOCARDLESS['webhook']['secret']
        calculated_signature = hmac.new(
            secret,
            msg=request.body,
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_signature, webhook_signature):
            return HttpResponse(
                status=self.INVALID_TOKEN
            )

        data = json.loads(request.body)
        events = data.get('events', None)

        if events is not None and isinstance(events, list):
            for event in events:
                EventHandler(Event(event, None))

            return HttpResponse(
                status=200
            )

        return HttpResponse(
            status=400
        )


class OAuthRedirectView(CSRFExemptView):

    def get(self, request, *args, **kwargs):
        for error in ['invalid_request', 'invalid_scope', 'unsupported_response_type']:
            if error in request.GET:
                return HttpResponseRedirect(
                    settings.GOCARDLESS['app']['redirect']['error']
                )

        if 'access_denied' in request.GET:
            return HttpResponseRedirect(
                settings.GOCARDLESS['app']['redirect']['error']
            )

        code = request.GET.get('code', None)
        state = request.GET.get('state', None)

        if code is None or state is None:
            return HttpResponseRedirect(
                settings.GOCARDLESS['app']['redirect']['error']
            )

        response = HttpResponse(
            status=307,  # Temporary redirect
        )
        response['Location'] = settings.GOCARDLESS['app']['redirect']['success']

        try:
            Merchant.exchange_authorisation(
                state=state,
                code=code
            )
        except ExchangeAuthorisationError:
            response['Location'] = settings.GOCARDLESS['app']['redirect']['error']

        return response
