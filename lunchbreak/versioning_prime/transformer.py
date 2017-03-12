from .transformation import Transformation


class Transformer:
    """Wrapper for applying transformations in the right order.

    .. note::
        I am Optimus Prime and I send this message to any surviving autobots
        taking refuge among the stars. We are here, we are waiting.
    """

    def __init__(self, *transformations):
        for transformation in transformations:
            assert isinstance(transformation, Transformation)
        self.transformations = list(transformations)

    def append(self, *transformations):
        for transformation in transformations:
            assert isinstance(transformation, Transformation)
        self.extend(transformations)

    def extend(self, transformations):
        self.transformations.extend(transformations)

    def transform(self, obj, data, request, forwards):
        self.transformations.sort()
        transformations = self.transformations \
            if forwards \
            else reversed(self.transformations)
        for transformation in transformations:
            try:
                result = transformation.transform(
                    obj=obj,
                    data=data,
                    request=request,
                    forwards=forwards
                )
                data = result
            except NotImplementedError:
                continue
        return data

    def backwards(self, obj, data, request):
        return self.transform(
            obj=obj,
            data=data,
            request=request,
            forwards=False
        )

    def forwards(self, obj, data, request):
        return self.transform(
            obj=obj,
            data=data,
            request=request,
            forwards=True
        )
