from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

COSTCHECK_FAILED = 700
PREORDERTIME_EXCEEDED = 701
PASTORDER_DENIED = 702
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


class PastOrderDenied(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PASTORDER_DENIED
    information = 'Een bestelling moet in de toekomst geplaatst worden.'


class CostCheckFailed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = COSTCHECK_FAILED
    information = 'Prijs komt niet overeen met berekende prijs.'


class PreorderTimeExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PREORDERTIME_EXCEEDED
    information = 'Een bestelling moet vroeger geplaatst worden.'


class StoreClosed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = STORE_CLOSED
    information = 'De winkel is gesloten op het gegeven moment.'


class AmountInvalid(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = AMOUNT_INVALID
    information = 'De hoeveelheid is ongeldig.'


class MinDaysExceeded(PreorderTimeExceeded):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MINDAYS_EXCEEDED
    # information see PreorderTimeExceeded


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
