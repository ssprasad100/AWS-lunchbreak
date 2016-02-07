from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

INVALID_EMAIL = 800
INCORRECT_PASSWORD = 801
INVALID_DATE = 802
INVALID_PASSWORD_RESET = 803


class InvalidEmail(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_EMAIL
    information = 'Invalid email address.'


class IncorrectPassword(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INCORRECT_PASSWORD
    information = 'Invalid password.'


class InvalidDatetime(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_DATE
    information = 'Invalid datetime.'


class InvalidPasswordReset(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_PASSWORD_RESET
    information = 'Invalid password reset token and email combination.'
