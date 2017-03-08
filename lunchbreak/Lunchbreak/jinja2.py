import logging

from jinja2 import Undefined

logger = logging.getLogger('lunchbreak')


def silently(*args, **kwargs):
    return ''


def recreate(*args, **kwargs):
    return SilencedUndefined()


class SilencedUndefined(Undefined):

    def _fail_with_undefined_error(self, *args, **kwargs):
        try:
            super()._fail_with_undefined_error(*args, **kwargs)
        except Exception as exception:
            logger.exception(
                str(exception),
                exc_info=True,
                extra={
                    '*args': args,
                    '**kwargs': kwargs
                }
            )

    def __str__(self, *args, **kwargs):
        self._fail_with_undefined_error(*args, **kwargs)
        return silently()

    __unicode__ = __str__

    def __call__(self, *args, **kwargs):
        self._fail_with_undefined_error(*args, **kwargs)
        return recreate()

    __getattr__ = __call__
