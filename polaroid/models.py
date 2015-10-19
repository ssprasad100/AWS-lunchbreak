from django.db import models
from imagekit.models import ImageSpecField
from pilkit.processors.resize import ResizeToCover
from polaroid.specs import HD, HQ, LQ, FullHD


class InvalidPolaroidSource(Exception):
    pass


class Polaroid(models.Model):

    class Meta:
        abstract = True

    @staticmethod
    def retrieve(original, versions, width, height, source=None):
        attr = source
        best = None
        for key, version in versions.iteritems():
            if version.width >= width and version.height >= height:
                if best is None or best.width > version.width:
                    best = version
                    attr = key

        return ((original if best is None else best), attr,)

    def retrieve_from_source(self, source, width, height):
        original = None
        versions = {}

        for key, value in self.__class__.__dict__.iteritems():
            if hasattr(value, 'field'):
                field = value.field
                if isinstance(field, ImageSpecField) and field.source == source:
                    spec = field.get_spec(source)
                    processors = spec.processors
                    for processor in processors:
                        if isinstance(processor, ResizeToCover):
                            versions[key] = processor
                elif key == source and isinstance(field, models.ImageField):
                    original = field

        if original is None:
            raise InvalidPolaroidSource()

        best, attr = Polaroid.retrieve(original, versions, width, height, source)

        return getattr(self, attr)


class PolaroidBase(Polaroid):
    original = models.ImageField(
        upload_to='polaroid_base'
    )
    full_hd = ImageSpecField(
        source='original',
        spec=FullHD
    )
    hd = ImageSpecField(
        source='original',
        spec=HD
    )
    hq = ImageSpecField(
        source='original',
        spec=HQ
    )
    lq = ImageSpecField(
        source='original',
        spec=LQ
    )
