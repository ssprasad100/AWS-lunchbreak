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
    information = 'Bad request.'


class AddressNotFound(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = ADDRESS_NOT_FOUND
    information = 'The address given could not be found.'


class DoesNotExist(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = DOES_NOT_EXIST
    information = 'Object does not exist.'


class IngredientGroupMaxExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INGR_GROUP_MAX_EXCEEDED
    information = 'IngredientGroup maximum exceeded.'


class IngredientGroupsMinimumNotMet(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INGR_GROUP_MIN_NOT_MET
    information = 'Minimum IngredientGroups not met.'


class LinkingError(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_LINKING
    information = 'Invalid model linking.'


class InvalidFoodTypeAmount(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_FOODTYPE_AMOUNT
    information = 'Invalid food type amount.'


class NoDeliveryToAddress(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = NO_DELIVERY_TO_ADDRESS
    information = 'Store does not deliver to given address.'
