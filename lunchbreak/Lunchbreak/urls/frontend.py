from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static

urlpatterns = patterns(
    '',
    url(
        r'^',
        include('frontend.urls')
    ),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
