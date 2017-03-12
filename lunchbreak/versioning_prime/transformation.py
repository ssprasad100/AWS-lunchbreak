from functools import total_ordering

from rest_framework.serializers import Field, Serializer

from .utils import get_version_index


@total_ordering
class Transformation:
    """An implied migration between versions.

    Transformations are sorted (and therefore applied) in the following order:
        * Same version
            * Fields first
            * Serializers second
        * Newer version
        * ...

    Attributes:
        bases: Fully qualified class names of serializers, fields or serializer's fielsd.
        version: The version transformed to.
        _version_index: Set automatically, is equal to the position of the
            version in the versioning class' ``alowed_versions``.

    .. note::
        ``bases`` can apply to either:
            * Serializers: ``myapp.serializers.MySerializer``.
            * Fields: ``myapp.fields.MyField``.
            * Serializer specific fields: ``myapp.serializers.MySerializer.field``
    """

    bases = []
    version = None

    _version_index = None

    def __new__(cls, *args, **kwargs):
        transformation = super().__new__(cls)
        transformation._version_index = get_version_index(transformation.version)
        return transformation

    def __init__(self, base, field=None):
        self.base = base
        self.field = field

    def __str__(self):
        return '{base}{field} {version}'.format(
            base=self.base.__name__,
            field='.{}'.format(self.field) if self.field else '',
            version=self.version
        )

    def __repr__(self):
        return '<{cls}: {str}>'.format(
            cls=self.__class__.__name__,
            str=self.__str__()
        )

    def __eq__(self, other):
        return self.is_same_version(other._version_index) \
            and self.field == other.field \
            and self.base == other.base

    def __lt__(self, other):
        if not self.is_same_version(other._version_index):
            return self.is_older_version(other._version_index)
        elif self.for_field:
            return False
        return self.for_specific_field and other.for_serializer

    @property
    def for_field(self):
        """Whether this transformation applies to a ``Field``.

        .. note::
            A ``Serializer`` inherits from ``Field``. What is meant with field
            here is a class that inherits from ``Field`` but does not inherit
            from ``Serializer``.

        Returns:
            True if the base is a ``Field`` subclass and no ``Serializer`` subclass.
            bool
        """
        return issubclass(self.base, Field) and not issubclass(self.base, Serializer)

    @property
    def for_specific_field(self):
        """Whether this transformation applies to a serializer's field.

        Returns:
            True if the base is a ``Serializer`` subclass and a specific field is set.
            bool
        """
        return self.field is not None and issubclass(self.base, Serializer)

    @property
    def for_serializer(self):
        """Whether this transforation applies to a field.

        Returns:
            True if the base is a ``Serializer`` and no specific field is set.
            bool
        """
        return self.field is None and issubclass(self.base, Serializer)

    def is_newer_version(self, version_index):
        return self._version_index > version_index

    def is_older_version(self, version_index):
        return self._version_index < version_index

    def is_same_version(self, version_index):
        return self._version_index == version_index

    def transform(self, obj, data, request, forwards):
        method_prefix = 'forwards_' if forwards else 'backwards_'
        if self.for_field:
            return getattr(self, method_prefix + 'field')(
                obj=obj,
                data=data,
                request=request
            )
        elif self.for_serializer:
            return getattr(self, method_prefix + 'serializer')(
                obj=obj,
                data=data,
                request=request
            )
        else:
            data[self.field] = getattr(self, method_prefix + 'specific_field')(
                obj=obj,
                data=data[self.field],
                request=request
            )
            return data

    def backwards_serializer(self, obj, data, request):
        raise NotImplementedError(
            'Transformation subclasses need to implement the backwards methods.'
        )

    def backwards_field(self, obj, data, request):
        raise NotImplementedError(
            'Transformation subclasses need to implement the backwards methods.'
        )

    def backwards_specific_field(self, obj, data, request):
        raise NotImplementedError(
            'Transformation subclasses need to implement the backwards methods.'
        )

    def forwards_serializer(self, obj, data, request):
        raise NotImplementedError(
            'Transformation subclasses need to implement the forwards methods.'
        )

    def forwards_field(self, obj, data, request):
        raise NotImplementedError(
            'Transformation subclasses need to implement the forwards methods.'
        )

    def forwards_specific_field(self, obj, data, request):
        raise NotImplementedError(
            'Transformation subclasses need to implement the forwards methods.'
        )
