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
    code = status.HTTP_400_BAD_REQUEST
    information = 'Foute ingeving.'


class AddressNotFound(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ADDRESS_NOT_FOUND
    information = 'Het gegeven adres kon niet gevonden worden.'


class DoesNotExist(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = DOES_NOT_EXIST
    information = 'Object bestaat niet.'


class IngredientGroupMaxExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INGR_GROUP_MAX_EXCEEDED
    information = 'Ingrediëntengroep maximum overschreden.'


class IngredientGroupsMinimumNotMet(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INGR_GROUP_MIN_NOT_MET
    information = 'Ingrediëntengroep minimum niet voldaan.'


class LinkingError(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_LINKING
    information = 'Fout bij linken objecten.'


class InvalidFoodTypeAmount(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_FOODTYPE_AMOUNT
    information = 'Ongeldig voedseltype hoeveelheid.'


class NoDeliveryToAddress(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = NO_DELIVERY_TO_ADDRESS
    information = 'Winkel levert niet aan opgegeven adres.'
