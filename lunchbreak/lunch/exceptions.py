from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

ADDRESS_NOT_FOUND = 601
DOES_NOT_EXIST = 602
INGR_GROUP_MAX_EXCEEDED = 603
INGR_GROUP_MIN_NOT_MET = 604
INVALID_LINKING = 605
INVALID_FOODTYPE_AMOUNT = 606
NO_DELIVERY_TO_ADDRESS = 607


class BadRequest(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Foute ingeving.'


class AddressNotFound(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ADDRESS_NOT_FOUND
    default_detail = 'Het gegeven adres kon niet gevonden worden.'


class DoesNotExist(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = DOES_NOT_EXIST
    default_detail = 'Object bestaat niet.'


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


class InvalidFoodTypeAmount(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_FOODTYPE_AMOUNT
    default_detail = 'Ongeldig voedseltype hoeveelheid.'


class NoDeliveryToAddress(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = NO_DELIVERY_TO_ADDRESS
    default_detail = 'Winkel levert niet aan opgegeven adres.'
