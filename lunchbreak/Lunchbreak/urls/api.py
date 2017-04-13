from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django_jinja import views

handler400 = views.BadRequest.as_view()
handler403 = views.PermissionDenied.as_view()
handler404 = views.PageNotFound.as_view()
handler500 = views.ServerError.as_view()

urlpatterns = [
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
        r'^payconiq/',
        include('payconiq.urls')
    ),
    url(
        r'^',
        include('private_media.urls')
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(
            r'^404/$',
            TemplateView.as_view(
                template_name='404.html'
            )
        ),
        url(
            r'^500/$',
            TemplateView.as_view(
                template_name='500.html'
            )
        ),
    ]
