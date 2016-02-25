from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.BusinessPage.as_view(),
        name='frontend-business'
    ),
    url(
        r'^users$',
        views.CustomersPage.as_view(),
        name='frontend-customers'
    ),
)
