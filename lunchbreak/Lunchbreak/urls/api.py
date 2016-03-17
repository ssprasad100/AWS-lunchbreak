from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(
        r'^aardappel/',
        include(admin.site.urls)
    ),
    url(
        r'^business/',
        include('business.urls.api')
    ),
    url(
        r'^customers/',
        include('customers.urls.api')
    ),
    url(
        r'^gocardless/',
        include('django_gocardless.urls')
    ),
    url(
        r'^',
        include('private_media.urls')
    ),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
