from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from twilio.request_validator import RequestValidator

from .conf import (PLIVO_AUTH_TOKEN, PLIVO_WEBHOOK_URL, TWILIO_AUTH_TOKEN,
                   TWILIO_WEBHOOK_URL)
from .models import Message
from .utils import validate_plivo_signature


class ValidatedView(View):

    def is_valid(self, request):
        raise NotImplementedError(
            'ValidatedView subclasses need to implement `is_valid`.'
        )

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if self.is_valid(request):
            return super().dispatch(request, *args, **kwargs)
        raise Http404()


class TwilioWebhookView(ValidatedView):

    def is_valid(self, request):
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        return validator.validate(
            uri=TWILIO_WEBHOOK_URL,
            params=request.POST,
            signature=request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
        )

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
                remote_uuid=message_id
            )
        except Message.DoesNotExist:
            raise Http404()

        message.handle_status(message_status)
        return HttpResponse(
            status=200
        )


class PlivoWebhookView(ValidatedView):

    def is_valid(self, request):
        return validate_plivo_signature(
            signature=request.META.get('HTTP_X_PLIVO_SIGNATURE', ''),
            post_params=request.POST,
            webhook_url=PLIVO_WEBHOOK_URL,
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
                gateway=Message.PLIVO,
                remote_uuid=message_id
            )
        except Message.DoesNotExist:
            raise Http404()

        message.handle_status(message_status)
        return HttpResponse(
            status=200
        )
