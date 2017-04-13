import json

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from rest_framework import status

from .models import Transaction


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


class WebhookView(ValidatedView):

    def is_valid(self, request):
        return True

        # signature = request.META.get('HTTP_X_SECURITY_SIGNATURE')
        # timestamp = request.META.get('HTTP_X_SECURITY_TIMESTAMP')
        # key = request.META.get('HTTP_X_SECURITY_KEY')
        # algorithm = request.META.get('HTTP_X_SECURITY_ALGORITHM')

        # print('request.META', request.META)
        # print('signature', signature)
        # print('timestamp', timestamp)
        # print('key', key)
        # print('algorithm', algorithm)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))

            if not isinstance(data, dict):
                return HttpResponseBadRequest(
                    'JSON must be a dictionary.'
                )
        except json.JSONDecodeError as e:
            return HttpResponseBadRequest(
                'Invalid JSON: ' + str(e)
            )

        transaction_remote_id = data.get('_id')
        transaction_status = data.get('status')

        if transaction_remote_id is None or transaction_status is None:
            return HttpResponseBadRequest(
                'JSON must contain an _id and status key.'
            )

        transaction = get_object_or_404(
            Transaction,
            remote_id=transaction_remote_id
        )
        transaction.status = transaction_status
        transaction.save()

        return HttpResponse(
            status=status.HTTP_200_OK
        )
