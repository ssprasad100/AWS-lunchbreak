from collections import defaultdict
from copy import deepcopy

from django.utils.functional import cached_property

from .transformer import Transformer
from .utils import get_version_index


class VersionedMixin:

    default_transformations = {
        'self': [],
        'fields': defaultdict(list),
    }

    @classmethod
    def add_transformation(cls, transformation, field=None):
        obj = transformation(cls, field=field)

        if not hasattr(cls, '_transformations'):
            cls._transformations = deepcopy(cls.default_transformations)

        if field is None:
            cls._transformations['self'].append(obj)
        else:
            cls._transformations['fields'][field].append(obj)

    @cached_property
    def _request(self):
        request = self.context.get('request')
        assert request is not None, \
            'No request passed in the context of {cls}.'.format(
                cls=self.__class__.__name__
            )
        assert hasattr(request, 'version'), \
            'No version passed in the request of {cls}.'.format(
                cls=self.__class__.__name__
        )
        return request

    @cached_property
    def version(self):
        return self._request.version

    @property
    def transformations(self):
        return getattr(self, '_transformations', deepcopy(self.default_transformations))

    def to_internal_value(self, data):
        obj = super().to_internal_value(data)

        return self.get_transformer(
            obj=obj,
            data=data,
            forwards=True,
        ).forwards(
            obj=obj,
            data=data,
            request=self._request
        )

    def to_representation(self, obj):
        data = super().to_representation(obj)

        return self.get_transformer(
            obj=obj,
            data=data,
            forwards=False,
        ).backwards(
            obj=obj,
            data=data,
            request=self._request
        )

    def get_transformations(self, forwards, field=None):
        if field is None:
            transformations = self.transformations['self']
        else:
            transformations = self.transformations['fields'][field]

        result = []
        version_index = get_version_index(self.version)
        for transformation in transformations:
            newer_version = transformation.is_newer_version(version_index)
            older_version = transformation.is_older_version(version_index)

            if forwards:
                if older_version:
                    result.append(transformation)
            else:
                if newer_version:
                    result.append(transformation)

        return result

    def get_transformer(self, obj, data, forwards):
        transformer = Transformer()

        if isinstance(data, dict):
            for key, value in data.items():
                transformations = self.get_transformations(
                    forwards=forwards,
                    field=key
                )
                transformer.extend(transformations)

        transformations = self.get_transformations(
            forwards=forwards
        )
        transformer.extend(transformations)

        return transformer
