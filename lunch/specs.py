from imagekit import ImageSpec
from imagekit.processors import ResizeToCover


class LDPI(ImageSpec):
    processors = [
        ResizeToCover(270, 120)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class MDPI(ImageSpec):
    processors = [
        ResizeToCover(360, 160)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class HDPI(ImageSpec):
    processors = [
        ResizeToCover(540, 240)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class XHDPI(ImageSpec):
    processors = [
        ResizeToCover(720, 320)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class XXHDPI(ImageSpec):
    processors = [
        ResizeToCover(1080, 480)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class XXXHDPI(ImageSpec):
    processors = [
        ResizeToCover(1440, 640)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }
