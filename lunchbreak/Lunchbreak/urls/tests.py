from django.conf.urls import include, url
from django_jinja import views

from . import frontend

handler400 = views.BadRequest.as_view()
handler403 = views.PermissionDenied.as_view()
handler404 = views.PageNotFound.as_view()
handler500 = views.ServerError.as_view()

urlpatterns = [
    url(
        r'',
        include(frontend)
    ),
]
