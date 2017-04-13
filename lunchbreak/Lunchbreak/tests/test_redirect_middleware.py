from django.test import RequestFactory
from django.test.utils import override_settings

from ..middleware import RedirectHostMiddleware
from .testcase import LunchbreakTestCase


class RedirectMiddlewareTestCase(LunchbreakTestCase):

    REDIRECT_FROM = 'lunchbreak.from'
    REDIRECT_TO = 'lunchbreak.to'

    @override_settings(
        ALLOWED_HOSTS=[
            REDIRECT_TO,
            REDIRECT_FROM,
        ],
        REDIRECTED_HOSTS={
            REDIRECT_FROM: REDIRECT_TO,
        }
    )
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()

        self.middleware = RedirectHostMiddleware()

    def test_redirect(self):
        self.request = self.factory.get(
            '/testerde/test/er/de/test/',
            HTTP_HOST=self.REDIRECT_FROM
        )

        response = self.middleware.process_request(self.request)
        self.assertEqual(
            response['Location'],
            '{scheme}://{host}{path}'.format(
                scheme=self.request.scheme,
                host=self.REDIRECT_TO,
                path=self.request.get_full_path()
            )
        )

    def test_redirect_port(self):
        self.request = self.factory.get(
            '/testerde/test/er/de/test/',
            HTTP_HOST=self.REDIRECT_FROM + ':8000'
        )

        response = self.middleware.process_request(self.request)
        self.assertEqual(
            response['Location'],
            '{scheme}://{host}{path}'.format(
                scheme=self.request.scheme,
                host=self.REDIRECT_TO + ':8000',
                path=self.request.get_full_path()
            )
        )

    def test_noredirect(self):
        self.request = self.factory.get(
            '/testerde/test/er/de/test/',
            HTTP_HOST=self.REDIRECT_TO
        )

        response = self.middleware.process_request(self.request)
        self.assertIsNone(response)

    def test_noredirect_port(self):
        self.request = self.factory.get(
            '/testerde/test/er/de/test/',
            HTTP_HOST=self.REDIRECT_TO + ':8000'
        )

        response = self.middleware.process_request(self.request)
        self.assertIsNone(response)
