from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Polaroid, PolaroidBase
from .specs import HD, HQ, LQ, FullHD


class PolaroidTestCase(TestCase):

    def setUp(self):
        self.image = SimpleUploadedFile('test.jpg', file('test.jpg').read())

    '''
    def test_retrieve_from_source(self):
        pol = PolaroidBase.objects.create(
            original=self.image
        )

        pol.retrieve_from_source('original', width=100, height=100)
    '''

    def test_retrieve(self):
        pol = PolaroidBase.objects.create(
            original=self.image
        )

        lq = LQ.processors[0]
        hq = HQ.processors[0]
        hd = HD.processors[0]
        full_hd = FullHD.processors[0]

        versions = {
            'lq': lq,
            'hq': hq,
            'hd': hd,
            'full_hd': full_hd
        }

        self.assertEquals(
            Polaroid.retrieve(
                original=pol.original,
                versions=versions,
                width=640,
                height=360
            ), (lq, 'lq',)
        )

        self.assertEquals(
            Polaroid.retrieve(
                original=pol.original,
                versions=versions,
                width=854,
                height=480
            ), (hq, 'hq',)
        )

        self.assertEquals(
            Polaroid.retrieve(
                original=pol.original,
                versions=versions,
                width=1280,
                height=720
            ), (hd, 'hd',)
        )

        self.assertEquals(
            Polaroid.retrieve(
                original=pol.original,
                versions=versions,
                width=1920,
                height=1080
            ), (full_hd, 'full_hd',)
        )
