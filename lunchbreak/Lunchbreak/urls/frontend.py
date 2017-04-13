from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django_jinja import views

handler400 = views.BadRequest.as_view()
handler403 = views.PermissionDenied.as_view()
handler404 = views.PageNotFound.as_view()
handler500 = views.ServerError.as_view()

urlpatterns = [
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
