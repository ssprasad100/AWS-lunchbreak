import logging

from django.apps import AppConfig
from django.conf import settings
from rest_framework.settings import import_from_string

logger = logging.getLogger(__name__)


class VersioningPrimeConfig(AppConfig):
    name = 'versioning_prime'
    verbose_name = 'Versioning Prime'

    @classmethod
    def get_allowed_versions(cls):
        if not hasattr(cls, '_allowed_versions'):
            drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
            versioning_class_name = drf_settings.get('DEFAULT_VERSIONING_CLASS', None)

            if versioning_class_name is None:
                raise NotImplementedError(
                    'A default versioning class needs to be defined in the DRF settings.'
                )

            versioning_class = import_from_string(
                versioning_class_name,
                setting_name='DEFAULT_VERSIONING_CLASS'
            )
            allowed_versions = getattr(versioning_class, 'allowed_versions', [])

            if not allowed_versions:
                raise NotImplementedError(
                    'No allowed_versions were available in the versioning class.'
                )

            if not isinstance(allowed_versions, list):
                raise TypeError(
                    'The allowed_versions in the versioning class needs to be a '
                    'list, order is important.'
                )
            cls._allowed_versions = allowed_versions
        return cls._allowed_versions

    def ready(self):
        if hasattr(self, 'ran'):
            return
        self.ran = True

        from .utils import generate_transformations

        generate_transformations()
