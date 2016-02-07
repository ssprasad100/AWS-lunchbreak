from rest_framework import status
from Lunchbreak.exceptions import LunchbreakException

ADDRESS_NOT_FOUND = 601
DOES_NOT_EXIST = 602
INGR_GROUP_MAX_EXCEEDED = 603
INGR_GROUP_MIN_NOT_MET = 604
INVALID_STORE_LINKING = 605
INVALID_INGREDIENT_LINKING = 607
INVALID_FOODTYPE_AMOUNT = 608


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


class InvalidStoreLinking(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_STORE_LINKING
    information = 'Invalid store linking.'


class InvalidIngredientLinking(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_INGREDIENT_LINKING
    information = 'Invalid ingredient linking.'


class InvalidFoodTypeAmount(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_FOODTYPE_AMOUNT
    information = 'Invalid food type amount.'
