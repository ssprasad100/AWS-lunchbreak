from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

COSTCHECK_FAILED = 700
PREORDERTIME_EXCEEDED = 701
PASTORDER_DENIED = 702
STORE_CLOSED = 704
# 705
MINDAYS_EXCEEDED = 706
USER_DISABLED = 707
# 708
# 709
# 710
# 711
ONLINE_PAYMENTS_DISABLED = 712
# 713
# 714
ORDEREDFOOD_NOT_ORIGINAL = 715
ONLINE_PAYMENT_REQUIRED = 716


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
    default_detail = 'Een bestelling moet langer op voorhand geplaatst worden.'


class StoreClosed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = STORE_CLOSED
    default_detail = 'De winkel is gesloten op het gegeven moment.'


class MinDaysExceeded(PreorderTimeExceeded):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = MINDAYS_EXCEEDED
    # information see PreorderTimeExceeded


class UserDisabled(LunchbreakException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = USER_DISABLED
    default_detail = 'Deze account werd uitgeschakeld.'


class OnlinePaymentDisabled(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ONLINE_PAYMENTS_DISABLED
    default_detail = 'Deze winkel heeft online betalingen uitgeschakeld.'


class OrderedFoodNotOriginal(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ORDEREDFOOD_NOT_ORIGINAL
    default_detail = 'Het originele waar moet gelijk zijn aan het meest aansluitende waar.'


class OnlinePaymentRequired(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ONLINE_PAYMENT_REQUIRED
    default_detail = 'Online betalen is verplicht bij deze bestelling.'
