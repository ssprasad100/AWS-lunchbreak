from Lunchbreak.responses import LunchbreakResponse
from rest_framework import status

INVALID_EMAIL = 800
INCORRECT_PASSWORD = 801


class InvalidEmail(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INVALID_EMAIL
    information = 'Invalid email address.'


class IncorrectPassword(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = INCORRECT_PASSWORD
    information = 'Invalid password.'
