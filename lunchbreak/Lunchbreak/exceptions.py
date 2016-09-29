from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.views import exception_handler


def lunchbreak_exception_handler(exception, context):
    response = exception_handler(exception, context)
    response.data = {
        'error': {
            'detail': response.data
        }
    }
    if exception is None:
        return response

    error_code = exception.code if hasattr(exception, 'code') else -1
    response.data['error']['code'] = error_code
    error_information = getattr(exception, 'information', None)

    if error_information is not None:
        response.data['error']['information'] = error_information

    status_code = getattr(
        exception.__class__,
        'status_code',
        None
    )
    if status_code is not None:
        response.status_code = status_code

    return response


class LunchbreakException(RestValidationError):

    def __init__(self, detail=None):
        super().__init__(detail)

    @property
    def response(self):
        return lunchbreak_exception_handler(self, None)

    @property
    def django_validation_error(self):
        return DjangoValidationError(self.detail)
