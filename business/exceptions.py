from lunch.exceptions import LunchbreakException
from rest_framework import status

INVALID_EMAIL = 800


class InvalidEmail(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_EMAIL
    information = 'Invalid email address.'
