from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def lunchbreak_exception_handler(exception, context):
    response = Response()
    response.data = {'error': {}}
    if exception is None:
        return response

    hasDetail = hasattr(exception, 'detail') and exception.detail is not None
    response.data['error']['code'] = exception.code if hasattr(exception, 'code') else -1
    if hasattr(exception, 'information'):
        response.data['error']['information'] = exception.information
        if hasDetail:
            response.data['error']['detail'] = exception.detail
    elif hasDetail:
        response.data['error']['information'] = exception.detail
    else:
        raise

    response.status_code = getattr(
        exception.__class__,
        'status_code',
        status.HTTP_400_BAD_REQUEST
    )

    return response


class LunchbreakException(ValidationError):

    def __init__(self, detail=None):
        if detail is None:
            super(LunchbreakException, self).__init__('No details.')
            self.detail = None
        elif not isinstance(detail, str):
            super(LunchbreakException, self).__init__(str(detail))
            self.detail = detail
        else:
            super(LunchbreakException, self).__init__(detail)

    @property
    def response(self):
        return lunchbreak_exception_handler(self, None)
