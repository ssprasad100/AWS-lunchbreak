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
ONLINE_PAYMENTS_DISABLED = 712
NO_PAYMENT_LINK = 713
PAYMENT_LINK_NOT_CONFIRMED = 714
ORDEREDFOOD_NOT_ORIGINAL = 715

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
    information = 'Een bestelling moet in de toekomst geplaatst worden.'


class CostCheckFailed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = COSTCHECK_FAILED
    information = 'Prijs komt niet overeen met berekende prijs.'


class MinTimeExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MINTIME_EXCEEDED
    information = 'Een bestelling moet vroegen geplaatst worden.'


class StoreClosed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = STORE_CLOSED
    information = 'De winkel is gesloten op het gegeven moment.'


class AmountInvalid(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = AMOUNT_INVALID
    information = 'De hoeveelheid is ongeldig.'


class MinDaysExceeded(MinTimeExceeded):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MINDAYS_EXCEEDED
    # information see MinTimeExceeded


class UserDisabled(LunchbreakException):
    status_code = status.HTTP_403_FORBIDDEN
    code = USER_DISABLED
    information = 'Deze account werd uitgeschakeld.'


class MaxSeatsExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MAX_SEATS_EXCEEDED
    information = 'De winkel heeft niet zoveel plaatsen beschikbaar.'


class NoInvitePermissions(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = NO_INVITE_PERMISSIONS
    information = 'Jij kan geen personen uitnodigen tot de groep.'


class AlreadyMembership(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ALREADY_MEMBERSHIP
    information = 'Gebruiker is al reeds lid van deze groep.'


class InvalidStatusChange(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_STATUS_CHANGE
    information = 'Foute status aanpassing.'


class OnlinePaymentDisabled(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ONLINE_PAYMENTS_DISABLED
    information = 'Deze winkel heeft online betalingen uitgeschakeld.'


class NoPaymentLink(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = NO_PAYMENT_LINK
    information = 'Gebruiker heeft geen mandaat met deze winkel getekend.'


class PaymentLinkNotConfirmed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PAYMENT_LINK_NOT_CONFIRMED
    information = 'Gebruiker heeft het mandaat nog niet bevestigd.'


class OrderedFoodNotOriginal(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ORDEREDFOOD_NOT_ORIGINAL
    information = 'Het originele waar moet gelijk zijn aan het meest aansluitende waar.'
