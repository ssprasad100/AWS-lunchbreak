from django.conf.urls import include, patterns, url

from . import api, frontend

urlpatterns = patterns(
    '',
    url(
        r'',
        include(api)
    ),
    url(
        r'',
        include(frontend)
    ),
)
