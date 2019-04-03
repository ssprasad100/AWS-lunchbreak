import inspect
import json
import sys
from json.decoder import JSONDecodeError


class PayconiqError(Exception):

    def __init__(self, message=None, response=None, json={}):
        super().__init__(message)

        if message is not None:
            self._message = message
        else:
            self._message = getattr(self, 'DEFAULT_MESSAGE', '<no message>')
        self.response = response
        self.json = json

    def __str__(self):
        return '{response}{message}{json}'.format(
            response='{method} {url}'.format(
                method=self.response.request.method,
                url=self.response.url,
            ) if self.response is not None else '',
            message='{}{}'.format(
                ', ' if self.response is not None else '',
                self.message
            ) if self.message else '',
            json=' ' + json.dumps(self.json, sort_keys=True, indent=2)
            if self.json else ''
        )

    @property
    def level(self):
        return self.json.get('level', None)

    @property
    def code(self):
        return self.json.get('code', None)

    @property
    def message(self):
        return self.json.get('message', self._message)

    @property
    def params(self):
        return self.json.get('params', None)

    @classmethod
    def _subclasses(cls):
        return [
            obj
            for name, obj in inspect.getmembers(sys.modules[__name__])
            if inspect.isclass(obj) and issubclass(obj, PayconiqError)
        ]

    @classmethod
    def from_response(cls, response):
        kwargs = {
            'response': response,
        }

        try:
            kwargs['json'] = response.json()
        except JSONDecodeError:
            pass

        subclasses = cls._subclasses()

        same_status = [
            subclass for subclass in subclasses
            if getattr(subclass, 'STATUS', None) == response.status_code
        ]
        amount_same_status = len(same_status)
        if amount_same_status == 0:
            return cls(**kwargs)
        elif amount_same_status == 1:
            return same_status[0](**kwargs)
        else:
            json_data = kwargs.get('json')
            if json_data is None:
                return same_status[0](**kwargs)
            code = json_data.get('code', None)
            if code is None:
                return same_status[0](**kwargs)

            same_code = [
                subclass for subclass in same_status
                if getattr(subclass, 'CODE', None) == code
            ]

            if len(same_code) == 0:
                return same_status[0](**kwargs)
            else:
                return same_code[0](**kwargs)


class InvalidRequestError(PayconiqError):

    def __init__(self, message, param, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.param = param


class BadRequestError(PayconiqError):
    STATUS = 400
    DEFAULT_MESSAGE = 'Bad request'


class OriginBlocked(BadRequestError):
    STATUS = 400
    CODE = 'R203'
    DEFAULT_MESSAGE = (
        'Transaction origin user bank account is blocked, it cannot be used'
    )


class TargetBlocked(BadRequestError):
    STATUS = 400
    CODE = 'R221'
    DEFAULT_MESSAGE = (
        'Transaction target user bank account is blocked, it cannot be used'
    )


class TargetNotValidated(BadRequestError):
    STATUS = 400
    CODE = 'R205'
    DEFAULT_MESSAGE = (
        'Transaction target user bank account is not validated yet, it '
        'cannot be used'
    )


class PreconditionFailed(PayconiqError):
    STATUS = 412
    DEFAULT_MESSAGE = 'Precondition failed'


class InternalServerError(PayconiqError):
    STATUS = 500
    DEFAULT_MESSAGE = 'Internal server error'
