import json
from datetime import timedelta

from django.contrib.auth.mixins import AccessMixin
from django.db.models import Q
from django.utils import timezone

from .models import Forward


class LoginForwardMixin(AccessMixin):

    forward_group = None

    def dispatch(self, request, *args, **kwargs):
        assert self.forward_group is not None, \
            'LoginForwardMixin subclasses need to set a forward_group.'

        if not request.user.is_authenticated():
            redirect_response = self.handle_no_permission()

            if request.method == 'POST' and request.POST:
                json_data = json.dumps(dict(request.POST))
                forward = Forward.objects.create(
                    group=self.forward_group,
                    json=json_data
                )
                redirect_response.set_cookie(
                    key='forward',
                    value=forward.id
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
