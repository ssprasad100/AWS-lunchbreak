from lunch.exceptions import LunchbreakException
from rest_framework import status

INVALID_DATE = 802


class InvalidDatetime(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_DATE
    information = 'Invalid datetime given.'
