from lunch.responses import LunchbreakResponse
from rest_framework import status

COSTCHECK_FAILED = 700
MINTIME_EXCEEDED = 701
PASTORDER_DENIED = 702


class CostCheckFailed(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = COSTCHECK_FAILED
    information = 'Cost check failed.'


class MinTimeExceeded(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = MINTIME_EXCEEDED
    information = 'An order must be placed later.'


class PastOrderDenied(LunchbreakResponse):
    status_code = status.HTTP_400_BAD_REQUEST
    code = PASTORDER_DENIED
    information = 'An order must be placed in the future.'
