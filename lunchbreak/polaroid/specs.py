from imagekit import ImageSpec
from imagekit.processors import ResizeToCover


class LQ(ImageSpec):
    processors = [
        ResizeToCover(640, 360)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class HQ(ImageSpec):
    processors = [
        ResizeToCover(854, 480)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class HD(ImageSpec):
    processors = [
        ResizeToCover(1280, 720)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }


class FullHD(ImageSpec):
    processors = [
        ResizeToCover(1920, 1080)
    ]
    format = 'JPEG'
    options = {
        'quality': 100
    }
