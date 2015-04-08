import logging

from lunch.exceptions import LunchbreakException
from rest_framework import status

COSTCHECK_FAILED = 700
MINTIME_EXCEEDED = 701
PASTORDER_DENIED = 702
DIGITS_UNAVAILABLE = 703
STORE_CLOSED = 704
AMOUNT_INVALID = 705

DIGITS_LEGACY_ERROR = 0
DIGITS_INVALID_PHONE = 32
DIGITS_APP_AUTH_ERROR = 89
DIGITS_PIN_INCORRECT = 236
DIGITS_GUEST_AUTH_ERROR = 239
DIGITS_ALREADY_REGISTERED_ERROR = 285

DIGITS_EXCEPTIONS = {
    DIGITS_LEGACY_ERROR: 'Digits legacy error.',
    DIGITS_INVALID_PHONE: ['Digits invalid phone number.', status.HTTP_400_BAD_REQUEST],
    DIGITS_APP_AUTH_ERROR: 'Digits app authorization failed.',
    DIGITS_GUEST_AUTH_ERROR: 'Digits guest authorization failed.',
    DIGITS_PIN_INCORRECT: ['Incorrect pin.', status.HTTP_400_BAD_REQUEST],
    DIGITS_ALREADY_REGISTERED_ERROR: 'User already in the Digits database.'
}


class DigitsException(LunchbreakException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = DIGITS_UNAVAILABLE
    information = 'Messaging service temporarily unavailable.'

    def __init__(self, code, content):
        detail = None
        if code in DIGITS_EXCEPTIONS:
            info = DIGITS_EXCEPTIONS[code]
            if type(info) is list:
                detail = info[0]
                self.status_code = info[1]
            else:
                detail = info
        else:
            logger = logging.getLogger(__name__)
            logger.exception('Undocumented Digits exception code %d: %s' % (code, content,))
        self.code = code
        super(DigitsException, self).__init__(detail)


class PastOrderDenied(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PASTORDER_DENIED
    information = 'An order must be placed in the future.'


class CostCheckFailed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = COSTCHECK_FAILED
    information = 'Cost check failed.'


class MinTimeExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MINTIME_EXCEEDED
    information = 'An order must be placed earlier.'


class StoreClosed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = STORE_CLOSED
    information = 'The store is closed.'


class AmountInvalid(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = AMOUNT_INVALID
    information = 'The amount is invalid.'
