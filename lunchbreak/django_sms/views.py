from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from plivo import validate_signature
from twilio.utils import RequestValidator

from .conf import PLIVO_AUTH_TOKEN, TWILIO_AUTH_TOKEN
from .models import Message


class CSRFExemptView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptView, self).dispatch(*args, **kwargs)


class ValidatedView(CSRFExemptView):

    def is_valid(self, request):
        raise NotImplementedError(
            'ValidatedView subclasses need to implement `is_valid`.'
        )

    def dispatch(self, request, *args, **kwargs):
        if self.is_valid(request):
            return super().dispatch(request, *args, **kwargs)
        raise Http404()


class TwilioWebhookView(ValidatedView):

    def post(self, request, *args, **kwargs):
        message_sid = request.POST.get('MessageSid', None)
        message_status = request.POST.get('MessageStatus', None)

        if message_sid is None or message_status is None:
            return HttpResponseBadRequest()

        message_id = message_sid[2:]

        try:
            message = Message.objects.select_related(
                'phone',
            ).get(
                id=message_id
            )
        except Message.DoesNotExist:
            raise Http404()

        message.handle_status(message_status)
        return HttpResponse(status=204)


class PlivoWebhookView(ValidatedView):

    def is_valid(self, request):
        return validate_signature(
            uri=request.build_absolute_uri(),
            post_params=request.POST,
            signature=request.META.get('HTTP_X_PLIVO_SIGNATURE', ''),
            auth_token=PLIVO_AUTH_TOKEN
        )

    def post(self, request, *args, **kwargs):
        message_id = request.POST.get('MessageUUID', None)
        message_status = request.POST.get('Status', None)

        if message_id is None or message_status is None:
            return HttpResponseBadRequest()

        try:
            message = Message.objects.select_related(
                'phone',
            ).get(
                id=message_id
            )
        except Message.DoesNotExist:
            raise Http404()

        message.handle_status(message_status)
        return HttpResponse(status=204)
