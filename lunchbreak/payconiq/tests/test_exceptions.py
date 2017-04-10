import payconiq
import responses
from payconiq import Transaction
from payconiq.exceptions import (BadRequestError, InternalServerError,
                                 OriginBlocked, PreconditionFailed,
                                 TargetBlocked, TargetNotValidated)

from .testcase import PayconiqTestCase


class ExceptionsTestCase(PayconiqTestCase):

    @responses.activate
    def assert_error_returned(self, error):
        kwargs = {
            'status': error.STATUS
        }
        code = getattr(error, 'CODE', None)
        if code is not None:
            kwargs['json'] = {
                'code': code
            }

        responses.add(
            responses.POST,
            payconiq.get_base_url(),
            **kwargs
        )

        self.assertRaises(
            error,
            Transaction.request,
            'POST',
            url=payconiq.get_base_url()
        )

    def test_exceptions(self):
        errors = (
            BadRequestError,
            InternalServerError,
            OriginBlocked,
            PreconditionFailed,
            TargetBlocked,
            TargetNotValidated,
        )
        for error in errors:
            self.assert_error_returned(error)
