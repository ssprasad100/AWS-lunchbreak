import json

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from rest_framework import status

from .models import Transaction
from .utils import is_signature_valid


class WebhookView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WebhookView, self).dispatch(*args, **kwargs)

    def is_valid(self, request, merchant_id):
        signature = request.META.get('HTTP_X_SECURITY_SIGNATURE')
        timestamp = request.META.get('HTTP_X_SECURITY_TIMESTAMP')
        key = request.META.get('HTTP_X_SECURITY_KEY')
        algorithm = request.META.get('HTTP_X_SECURITY_ALGORITHM')

        if signature is None \
                or merchant_id is None \
                or timestamp is None \
                or key is None \
                or algorithm is None:
            return False

        return is_signature_valid(
            signature=signature,
            merchant_id=merchant_id,
            timestamp=timestamp,
            algorithm=algorithm,
            body=request.body
        )

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
            Transaction.objects.select_related(
                'merchant'
            ),
            remote_id=transaction_remote_id
        )

        if not self.is_valid(request, transaction.merchant.remote_id):
            raise Http404()

        transaction.status = transaction_status
        transaction.save()

        return HttpResponse(
            status=status.HTTP_200_OK
        )
