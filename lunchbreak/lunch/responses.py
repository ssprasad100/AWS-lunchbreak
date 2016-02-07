from Lunchbreak.responses import LunchbreakResponse
from rest_framework import status

AUTHENTICATION_FAILED = 600
DOES_NOT_EXIST = 602
WRONG_API_VERSION = 606


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
