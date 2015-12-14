import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView, View
from gocardless_pro.resources import Event

from .exceptions import (BadRequest, DjangoGoCardlessException,
                         RedirectFlowAlreadyCompleted, RedirectFlowIncomplete)
from .handlers import EventHandler
from .models import RedirectFlow


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
        response['Location'] = settings.GOCARDLESS['app_redirect']
        if redirectflow_id is not None:
            try:
                redirectflow = RedirectFlow.objects.get(
                    id=redirectflow_id
                )
                redirectflow.complete()
                response['Location'] = settings.GOCARDLESS['app_redirect']['success']
            except (RedirectFlow.DoesNotExist, DjangoGoCardlessException) as e:
                if isinstance(e, RedirectFlowIncomplete):
                    response['Location'] = settings.GOCARDLESS[
                        'app_redirect']['error']['incomplete']
                elif isinstance(e, RedirectFlowAlreadyCompleted):
                    response['Location'] = settings.GOCARDLESS[
                        'app_redirect']['error']['completed']
                elif isinstance(e, BadRequest):
                    response['Location'] = settings.GOCARDLESS['app_redirect']['error']['invalid']
                else:
                    response['Location'] = settings.GOCARDLESS['app_redirect']['error']['default']

        return response


class CSRFExemptView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class WebhookView(CSRFExemptView):

    INVALID_TOKEN = 498

    def post(self, request, *args, **kwargs):
        try:
            webhook_signature = request.META.get('HTTP_WEBHOOK_SIGNATURE', None)

            if webhook_signature is None:
                return HttpResponse(
                    status=self.INVALID_TOKEN
                )

            calculated_signature = hmac.new(
                settings.GOCARDLESS['webhook']['secret'],
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
        except ValueError:
            pass

        return HttpResponse(
            status=400
        )
