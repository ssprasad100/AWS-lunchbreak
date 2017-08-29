from collections import defaultdict
from copy import deepcopy

from django.utils.functional import cached_property

from .transformer import Transformer
from .utils import get_version_index


class VersionedMixin:

    default_transformation_classes = {
        'self': [],
        'field_names': defaultdict(list),
    }

    @classmethod
    def add_transformation(cls, transformation_class, field_name=None):
        if not hasattr(cls, '_transformation_classes'):
            cls._transformation_classes = deepcopy(cls.default_transformation_classes)

        if field_name is None:
            cls._transformation_classes['self'].append(transformation_class)
        else:
            cls._transformation_classes['field_names'][field_name].append(transformation_class)

    @cached_property
    def _request(self):
        request = self.context.get('request')
        assert request is not None, \
            'No request passed in the context of {cls}: {context}'.format(
                cls=self.__class__.__name__,
                context=self.context
            )
        assert hasattr(request, 'version'), \
            'No version passed in the request of {cls}: {context}'.format(
                cls=self.__class__.__name__,
                context=self.context
        )
        return request

    @cached_property
    def version(self):
        return self._request.version

    @property
    def transformation_classes(self):
        return getattr(
            self,
            '_transformation_classes',
            deepcopy(self.default_transformation_classes)
        )

    def to_internal_value(self, data):
        transformed_data = self.get_transformer(
            data=data,
            forwards=True,
        ).forwards(
            obj=None,
            data=data,
            request=self._request
        )

        return super().to_internal_value(transformed_data)

    def to_representation(self, obj):
        data = super().to_representation(obj)

        return self.get_transformer(
            data=data,
            forwards=False,
        ).backwards(
            obj=obj,
            data=data,
            request=self._request
        )

    def get_transformations(self, forwards, field=None):
        if field is None:
            transformation_classes = self.transformation_classes['self']
        else:
            transformation_classes = self.transformation_classes['field_names'][field.field_name]

        result = []
        version_index = get_version_index(self.version)
        for transformation_class in transformation_classes:
            transformation = transformation_class(self, field=field)
            newer_version = transformation.is_newer_version(version_index)

            if newer_version:
                result.append(transformation)

        return result

    def get_transformer(self, data, forwards):
        transformer = Transformer()

        if isinstance(data, dict):
            for key, value in data.items():
                if key not in self.fields:
                    continue
                field = self.fields[key]
                transformations = self.get_transformations(
                    forwards=forwards,
                    field=field
                )
                transformer.extend(transformations)

        transformations = self.get_transformations(
            forwards=forwards
        )
        transformer.extend(transformations)

        return transformer
