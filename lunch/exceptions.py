from rest_framework.exceptions import APIException
from rest_framework import status


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, please try again later.'


class DigitsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Messaging service temporarily unavailable, please try again later.'


class InvalidRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid request paramaters.'


class AddressNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The address given could not be found.'


class DoesNotExist(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Object does not exist.'
