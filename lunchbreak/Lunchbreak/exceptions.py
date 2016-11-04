import logging
import traceback

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('lunchbreak')


def lunchbreak_exception_handler(exception, context):
    response = exception_handler(exception, context)

    handled = response is not None

    if not handled:
        response = Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            exception=exception
        )

    error = {
        'detail': None
    }
    if response.data is not None:
        if isinstance(response.data, dict) and 'detail' in response.data:
            error = response.data
        else:
            if isinstance(response.data, list) and len(response.data) == 1:
                error['detail'] = response.data[0]
            else:
                error['detail'] = response.data
    else:
        error['detail'] = str(exception)
    response.data = {
        'error': error
    }

    if exception is None:
        return response

    response.data['error']['code'] = getattr(exception, 'default_code', -1)

    if not settings.DEBUG and not handled and response.data['error']['code'] == -1:
        logger.exception(
            str(exception),
            exc_info=True,
            extra={
                'response': response,
                'context': context
            }
        )
    if settings.DEBUG:
        traceback.print_exc()

    return response


class LunchbreakException(RestValidationError):

    default_code = -1

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail
        super().__init__(detail)

    @property
    def response(self):
        return lunchbreak_exception_handler(self, None)

    @property
    def django_validation_error(self):
        return DjangoValidationError(
            self.information if self.detail is None else self.detail
        )
