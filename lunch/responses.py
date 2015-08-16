from rest_framework import status
from rest_framework.response import Response
from lunch.exceptions import lunchbreakExceptionHandler

AUTHENTICATION_FAILED = 600
DOES_NOT_EXIST = 602
WRONG_API_VERSION = 606


class LunchbreakResponse(Response):

    def __init__(self, detail=None, status_code=None, exception=None, template_name=None, headers=None, content_type=None):
        if exception is None:
            status_code = self.status_code if status_code is None else status_code
            data = {
                'error': {
                    'code': self.code,
                    'information': self.information
                }
            }

            if detail is not None:
                data['error']['detail'] = detail
        else:
            response = lunchbreakExceptionHandler(exception)
            data = response.data

        super(LunchbreakResponse, self).__init__(data, status_code, template_name, headers, content_type)


class BadRequest(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = status.HTTP_400_BAD_REQUEST
    information = 'Bad request.'


class DoesNotExist(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = DOES_NOT_EXIST
    information = 'Object does not exist.'


class WrongAPIVersion(LunchbreakResponse):
    status_code = status.HTTP_301_MOVED_PERMANENTLY
    code = WRONG_API_VERSION
    information = 'API Version not supported.'
