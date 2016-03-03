import logging

from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

COSTCHECK_FAILED = 700
MINTIME_EXCEEDED = 701
PASTORDER_DENIED = 702
DIGITS_UNAVAILABLE = 703
STORE_CLOSED = 704
AMOUNT_INVALID = 705
MINDAYS_EXCEEDED = 706
USER_DISABLED = 707
MAX_SEATS_EXCEEDED = 708
NO_INVITE_PERMISSIONS = 709
ALREADY_MEMBERSHIP = 710
INVALID_STATUS_CHANGE = 711

DIGITS_UNKNOWN = -1
DIGITS_LEGACY_ERROR = 0
DIGITS_INVALID_PHONE = 32
DIGITS_INVALID_PIN = 44
DIGITS_CLIENT_NOT_PRIVILIGED = 87
DIGITS_RATE_LIMIT_EXCEEDED = 88
DIGITS_APP_AUTH_ERROR = 89
DIGITS_OVER_CAPACITY = 130
DIGITS_EXPIRED = 235
DIGITS_PIN_INCORRECT = 236
DIGITS_MISSING_LOGIN_VERIFICATION = 237
DIGITS_GUEST_AUTH_ERROR = 239
DIGITS_SPAMMER = 240
DIGITS_NO_SDK_USER = 269
DIGITS_ALREADY_REGISTERED_ERROR = 285
DIGITS_OPERATOR_UNSUPPORTED = 286
DIGITS_DEVICE_RATE_EXCEEDED = 299
DIGITS_GENERAL_ERROR = 300
DIGITS_OPERATION_FAILED = 302
DIGITS_NORMALISATION_FAILED = 303

DIGITS_EXCEPTIONS = {
    DIGITS_UNKNOWN: 'Unknown error.',
    DIGITS_LEGACY_ERROR: 'Legacy error.',
    DIGITS_INVALID_PHONE: [
        'Invalid phone number.',
        status.HTTP_400_BAD_REQUEST
    ],
    DIGITS_INVALID_PIN: [
        'Invalid pin.',
        status.HTTP_400_BAD_REQUEST
    ],
    DIGITS_CLIENT_NOT_PRIVILIGED: 'Client not privileged.',
    DIGITS_RATE_LIMIT_EXCEEDED: 'Rate limit exceeded.',
    DIGITS_APP_AUTH_ERROR: 'App authorisation failed.',
    DIGITS_OVER_CAPACITY: 'Over capacity.',
    DIGITS_EXPIRED: 'Pin expired.',
    DIGITS_PIN_INCORRECT: [
        'Incorrect pin.',
        status.HTTP_400_BAD_REQUEST
    ],
    DIGITS_MISSING_LOGIN_VERIFICATION: [
        'Missing login verification request.',
        status.HTTP_400_BAD_REQUEST
    ],
    DIGITS_GUEST_AUTH_ERROR: 'Guest authorization failed.',
    DIGITS_SPAMMER: 'Spammer.',
    DIGITS_NO_SDK_USER: 'User is no SDK user.',
    DIGITS_ALREADY_REGISTERED_ERROR: 'User already registered.',
    DIGITS_OPERATOR_UNSUPPORTED: [
        'Phone operator not supported.',
        status.HTTP_400_BAD_REQUEST
    ],
    DIGITS_DEVICE_RATE_EXCEEDED: 'Device registration rate exceeded.',
    DIGITS_GENERAL_ERROR: 'General error.',
    DIGITS_OPERATION_FAILED: 'Operation failed.',
    DIGITS_NORMALISATION_FAILED: 'Phone normalisation failed.',
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


class MinDaysExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MINDAYS_EXCEEDED
    information = 'An order must be placed earlier.'


class UserDisabled(LunchbreakException):
    status_code = status.HTTP_403_FORBIDDEN
    code = USER_DISABLED
    information = 'Your account has been disabled.'


class MaxSeatsExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MAX_SEATS_EXCEEDED
    information = 'The amount of seats exceeds the store\'s maximum.'


class NoInvitePermissions(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = NO_INVITE_PERMISSIONS
    information = 'You cannot invite a user to this group.'


class AlreadyMembership(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ALREADY_MEMBERSHIP
    information = 'User already a member of the specified group.'


class InvalidStatusChange(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_STATUS_CHANGE
    information = 'Invalid status change.'
