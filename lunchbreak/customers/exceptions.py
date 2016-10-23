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
    default_code = PASTORDER_DENIED
    default_detail = 'Een bestelling moet in de toekomst geplaatst worden.'


class CostCheckFailed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = COSTCHECK_FAILED
    default_detail = 'Prijs komt niet overeen met berekende prijs.'


class PreorderTimeExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PREORDERTIME_EXCEEDED
    default_detail = 'Een bestelling moet vroeger geplaatst worden.'


class StoreClosed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = STORE_CLOSED
    default_detail = 'De winkel is gesloten op het gegeven moment.'


class AmountInvalid(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = AMOUNT_INVALID
    default_detail = 'De hoeveelheid is ongeldig.'


class MinDaysExceeded(PreorderTimeExceeded):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = MINDAYS_EXCEEDED
    # information see PreorderTimeExceeded


class UserDisabled(LunchbreakException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = USER_DISABLED
    default_detail = 'Deze account werd uitgeschakeld.'


class MaxSeatsExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = MAX_SEATS_EXCEEDED
    default_detail = 'De winkel heeft niet zoveel plaatsen beschikbaar.'


class NoInvitePermissions(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = NO_INVITE_PERMISSIONS
    default_detail = 'Jij kan geen personen uitnodigen tot de groep.'


class AlreadyMembership(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ALREADY_MEMBERSHIP
    default_detail = 'Gebruiker is al reeds lid van deze groep.'


class InvalidStatusChange(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_STATUS_CHANGE
    default_detail = 'Foute status aanpassing.'


class OnlinePaymentDisabled(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ONLINE_PAYMENTS_DISABLED
    default_detail = 'Deze winkel heeft online betalingen uitgeschakeld.'


class NoPaymentLink(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = NO_PAYMENT_LINK
    default_detail = 'Gebruiker heeft geen mandaat met deze winkel getekend.'


class PaymentLinkNotConfirmed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PAYMENT_LINK_NOT_CONFIRMED
    default_detail = 'Gebruiker heeft het mandaat nog niet bevestigd.'


class OrderedFoodNotOriginal(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ORDEREDFOOD_NOT_ORIGINAL
    default_detail = 'Het originele waar moet gelijk zijn aan het meest aansluitende waar.'
