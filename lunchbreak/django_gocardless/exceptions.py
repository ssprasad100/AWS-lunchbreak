
class DjangoGoCardlessException(Exception):

    @classmethod
    def from_gocardless_exception(cls, exception):
        try:
            errors = exception.errors

            for error in errors:
                if hasattr(error, 'reason'):
                    if error.reason in exception_reasons:
                        return exception_reasons[error.reason]
        except AttributeError:
            pass
        return cls(exception)


class ExchangeAuthorisationException(DjangoGoCardlessException):
    pass


class RedirectFlowCompleteException(DjangoGoCardlessException):
    pass


class RedirectFlowIncomplete(DjangoGoCardlessException):
    pass


class RedirectFlowAlreadyCompleted(DjangoGoCardlessException):
    pass


class BadRequest(DjangoGoCardlessException):
    pass


class UnsupportedEvent(DjangoGoCardlessException):
    pass


class UnsupportedLinks(DjangoGoCardlessException):
    pass


class AccessDenied(DjangoGoCardlessException):
    pass


exception_reasons = {
    'redirect_flow_incomplete': RedirectFlowIncomplete,
    'redirect_flow_already_completed': RedirectFlowAlreadyCompleted,
    'bad_request': BadRequest
}
