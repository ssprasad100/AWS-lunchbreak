from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

ADDRESS_NOT_FOUND = 601
INGR_GROUP_MAX_EXCEEDED = 603
INGR_GROUP_MIN_NOT_MET = 604
INVALID_LINKING = 605
UNSUPPORTED_API_VERSION = 606
INVALID_FOODTYPE_AMOUNT = 607
NO_DELIVERY_TO_ADDRESS = 608


class AddressNotFound(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ADDRESS_NOT_FOUND
    default_detail = 'Het gegeven adres kon niet gevonden worden.'


class IngredientGroupMaxExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INGR_GROUP_MAX_EXCEEDED
    default_detail = 'Ingrediëntengroep maximum overschreden.'


class IngredientGroupsMinimumNotMet(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INGR_GROUP_MIN_NOT_MET
    default_detail = 'Ingrediëntengroep minimum niet voldaan.'


class LinkingError(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_LINKING
    default_detail = 'Fout bij linken objecten.'


class UnsupportedAPIVersion(LunchbreakException):
    status_code = status.HTTP_301_MOVED_PERMANENTLY
    default_code = UNSUPPORTED_API_VERSION
    default_detail = 'API Version not supported.'


class InvalidFoodTypeAmount(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_FOODTYPE_AMOUNT
    default_detail = 'Ongeldig voedseltype hoeveelheid.'


class NoDeliveryToAddress(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = NO_DELIVERY_TO_ADDRESS
    default_detail = 'Winkel levert niet aan opgegeven adres.'
