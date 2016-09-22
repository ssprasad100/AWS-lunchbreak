from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

UNKNOWN_ERROR = 0
PIN_EXPIRED = 235
PIN_INCORRECT = 236
PIN_TIMEOUT = 299


class SmsException(LunchbreakException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = UNKNOWN_ERROR
    information = 'Unknown error.'


class PinExpired(SmsException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PIN_EXPIRED
    information = 'Given pin code has expired.'


class PinTriesExceeded(PinExpired):
    information = 'Max amount of pin tries exceeded.'


class PinIncorrect(SmsException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PIN_INCORRECT
    information = 'Given pin code is incorrect.'


class PinTimeout(SmsException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PIN_TIMEOUT
    information = 'Given pin code is incorrect.'
