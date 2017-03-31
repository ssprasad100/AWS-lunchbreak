import inspect
import sys

from gocardless_pro.errors import ApiError, GoCardlessProError


class DjangoGoCardlessException(Exception):

    def __init__(self, reason=None):
        message = '{message} ({reason})'.format(
            message=getattr(self, 'message', 'No message supplied'),
            reason=reason
        )
        return super(DjangoGoCardlessException, self).__init__(message)

    @classmethod
    def _subclasses(cls):
        return [
            obj
            for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
            if issubclass(obj, DjangoGoCardlessException)
        ]

    @classmethod
    def from_gocardless_exception(cls, exception):
        if not issubclass(exception.__class__, GoCardlessProError):
            raise NotImplementedError(
                '{cls} does not support non {gc} classes.'.format(
                    cls=cls.__name__,
                    gc=GoCardlessProError.__name__
                )
            )
        if not issubclass(exception.__class__, ApiError):
            return cls(exception)

        errors = exception.errors
        subclasses = cls._subclasses()

        for error in errors:
            if 'reason' in error:
                reason = error['reason']
                for subclass in subclasses:
                    if hasattr(subclass, 'reasons') and reason in subclass.reasons:
                        return subclass(reason)
        return cls(exception)


class ExchangeAuthorisationError(DjangoGoCardlessException):
    message = 'Error exchanging authorisation.'


class RedirectFlowIncompleteError(DjangoGoCardlessException):
    message = 'RedirectFlow not yet completed'
    reasons = [
        'redirect_flow_incomplete'
    ]


class RedirectFlowAlreadyCompletedError(DjangoGoCardlessException):
    message = 'RedirectFlow has already been completed.'
    reasons = [
        'redirect_flow_already_completed'
    ]


class BadRequestError(DjangoGoCardlessException):
    message = 'Check request data.'
    reasons = [
        'bad_request'
    ]


class UnsupportedEventError(DjangoGoCardlessException):
    message = 'Event is not supported by Django GoCardless.'


class UnsupportedLinksError(DjangoGoCardlessException):
    message = 'Model not supported by Django GoCardless.'


class MerchantAccessError(DjangoGoCardlessException):
    message = 'Merchant API access denied, check access token.'
    reasons = [
        'access_token_not_active',
        'access_token_not_found'
    ]


class LinkedMerchantDoesNotExist(DjangoGoCardlessException):
    message = 'Organisation in links does not exist.'
