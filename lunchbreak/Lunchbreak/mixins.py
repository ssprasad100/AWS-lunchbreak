from django.core.exceptions import ValidationError

from .exceptions import LunchbreakException


class CleanModelMixin:

    def clean(self, form=None):
        fields = self.__class__._meta.get_fields()

        for field in fields:
            clean_method_name = 'clean_{}'.format(field.name)
            if hasattr(self, clean_method_name):
                try:
                    getattr(self, clean_method_name)()
                except Exception as e:
                    if form is None:
                        raise

                    validation_error = None
                    if isinstance(e, ValidationError):
                        validation_error = e
                    elif isinstance(e, LunchbreakException):
                        validation_error = e.django_validation_error
                    else:
                        raise

                    form.add_error(field.name, validation_error)
