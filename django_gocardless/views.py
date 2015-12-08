from django.conf import settings
from django.http import HttpResponse
from django.views.generic.base import RedirectView, View
from django_gocardless.exceptions import (BadRequest,
                                          DjangoGoCardlessException,
                                          RedirectFlowAlreadyCompleted,
                                          RedirectFlowIncomplete)
from django_gocardless.models import RedirectFlow


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
                    response['Location'] = settings.GOCARDLESS['app_redirect']['error']['incomplete']
                elif isinstance(e, RedirectFlowAlreadyCompleted):
                    response['Location'] = settings.GOCARDLESS['app_redirect']['error']['completed']
                elif isinstance(e, BadRequest):
                    response['Location'] = settings.GOCARDLESS['app_redirect']['error']['invalid']
                else:
                    response['Location'] = settings.GOCARDLESS['app_redirect']['error']['default']

        return response
