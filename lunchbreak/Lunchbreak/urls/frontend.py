from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static

urlpatterns = patterns(
    '',
    url(
        r'^gocardless/',
        include('django_gocardless.urls')
    ),
    url(
        r'^api/',
        include('Lunchbreak.urls.api')
    ),
    url(
        r'^',
        include('frontend.urls')
    ),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
