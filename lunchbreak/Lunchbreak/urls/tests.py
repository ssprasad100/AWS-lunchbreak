from django.conf.urls import include, patterns, url
from django_jinja import views

from . import api, frontend

handler400 = views.BadRequest.as_view()
handler403 = views.PermissionDenied.as_view()
handler404 = views.PageNotFound.as_view()
handler500 = views.ServerError.as_view()

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
