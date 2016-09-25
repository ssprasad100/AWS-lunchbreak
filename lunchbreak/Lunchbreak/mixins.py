from django.core.exceptions import ValidationError

from .exceptions import LunchbreakException


class CleanModelMixin:

    def clean(self):
        fields = self.__class__._meta.get_fields()

        for field in fields:
            clean_method_name = 'clean_{}'.format(field.name)
            if hasattr(self, clean_method_name):
                try:
                    getattr(self, clean_method_name)()
                except Exception as e:
                    form = getattr(self, '_form', None)
                    if form is None:
                        raise

                    if isinstance(e, LunchbreakException):
                        e = e.django_validation_error
                    elif not isinstance(e, ValidationError):
                        raise

                    form.add_error(
                        field.name,
                        e
                    )
