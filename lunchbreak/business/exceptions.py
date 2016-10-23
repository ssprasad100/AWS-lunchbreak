from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

INVALID_EMAIL = 800
INCORRECT_PASSWORD = 801
INVALID_DATE = 802
INVALID_PASSWORD_RESET = 803


class InvalidEmail(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_EMAIL
    default_detail = 'Ongeldig e-mailadres.'


class IncorrectPassword(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INCORRECT_PASSWORD
    default_detail = 'Ongeldig wachtwoord.'


class InvalidDatetime(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_DATE
    default_detail = 'Ongeldige tijd.'


class InvalidPasswordReset(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = INVALID_PASSWORD_RESET
    default_detail = 'Ongeldige wachtwoord reset token en e-mailadres combinatie.'
