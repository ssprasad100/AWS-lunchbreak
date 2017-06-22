from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

UNKNOWN_ERROR = 0
PIN_EXPIRED = 235
PIN_INCORRECT = 236
PIN_TIMEOUT = 299


class SmsException(LunchbreakException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = UNKNOWN_ERROR
    default_detail = 'Unknown error.'


class PinExpired(SmsException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PIN_EXPIRED
    default_detail = 'Given pin code has expired.'


class PinTriesExceeded(PinExpired):
    default_detail = 'Max amount of pin tries exceeded.'


class PinIncorrect(SmsException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PIN_INCORRECT
    default_detail = 'Given pin code is incorrect.'


class PinTimeout(SmsException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PIN_TIMEOUT
    default_detail = 'A pin cannot be requested that quickly after another.'
