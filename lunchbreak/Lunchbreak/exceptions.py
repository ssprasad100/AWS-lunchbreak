from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.views import exception_handler


def lunchbreak_exception_handler(exception, context):

    response = exception_handler(exception, context)
    if isinstance(response.data, list):
        response.data = {
            'information': response.data
        }
    elif 'detail' in response.data:
        response.data['information'] = response.data.pop('detail')
    response.data = {
        'error': response.data
    }
    if exception is None:
        return response

    has_detail = hasattr(exception, 'detail') and exception.detail is not None
    response.data['error']['code'] = exception.code if hasattr(exception, 'code') else -1
    if hasattr(exception, 'information'):
        response.data['error']['information'] = exception.information
        if has_detail:
            response.data['error']['detail'] = exception.detail
    elif has_detail:
        response.data['error']['information'] = exception.detail

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
        if detail is None:
            super().__init__(self.information)
        else:
            super().__init__(detail)

    @property
    def response(self):
        return lunchbreak_exception_handler(self, None)

    @property
    def django_validation_error(self):
        return DjangoValidationError(self.detail)
