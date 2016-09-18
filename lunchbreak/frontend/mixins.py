import json
from datetime import timedelta

from django.contrib.auth.mixins import AccessMixin
from django.db.models import Q
from django.http.request import QueryDict
from django.utils import timezone

from .models import Forward


class ForwardMixin:

    forward_group = None

    def dispatch(self, request, *args, **kwargs):
        assert self.forward_group is not None, \
            'ForwardMixin subclasses need to set a forward_group.'

        if self.should_forward(request, *args, **kwargs):
            redirect_response = self.get_redirect_response(
                request, *args, **kwargs
            )

            if request.method == 'POST' and request.POST:
                redirect_response = self.create_forward(
                    request=request,
                    response=redirect_response
                )

            return redirect_response

        forward_id = request.COOKIES.get('forward')
        if forward_id is not None:
            try:
                forward = Forward.objects.get(
                    id=forward_id
                )
                request.forward_data = json.loads(forward.json)
                Forward.objects.filter(
                    Q(created_at__gt=timezone.now() + timedelta(days=1)) |
                    Q(pk=forward.pk)
                ).delete()
            except Forward.DoesNotExist:
                pass

        return super().dispatch(
            request, *args, **kwargs
        )

    def create_forward(self, request, response, data=None):
        if data is None:
            data = request.POST

        if isinstance(data, QueryDict):
            data = dict(data)

        json_data = json.dumps(data)
        forward = Forward.objects.create(
            group=self.forward_group,
            json=json_data
        )
        response.set_cookie(
            key='forward',
            value=forward.id
        )
        return response

    def should_forward(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_redirect_response(self, request, *args, **kwargs):
        raise NotImplementedError()


class LoginForwardMixin(ForwardMixin, AccessMixin):

    def should_forward(self, request, *args, **kwargs):
        return not request.user.is_authenticated()

    def get_redirect_response(self, request, *args, **kwargs):
        return self.handle_no_permission()
