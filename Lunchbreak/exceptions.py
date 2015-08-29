from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response


def lunchbreakExceptionHandler(exception, context):
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

    response.status_code = exception.status_code if hasattr(exception, 'status_code') else status.HTTP_400_BAD_REQUEST
    return response


class LunchbreakException(APIException):

    def __init__(self, detail=None):
        if detail is None:
            super(LunchbreakException, self).__init__()
            self.detail = None
        elif not isinstance(detail, basestring):
            super(LunchbreakException, self).__init__()
            self.detail = detail
        else:
            super(LunchbreakException, self).__init__(detail)

    def getResponse(self):
        return lunchbreakExceptionHandler(self, None)