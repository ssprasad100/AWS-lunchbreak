from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.IndexView.as_view(),
        name='frontend-index'
    ),
    url(
        r'^search/?$',
        views.SearchView.as_view(),
        name='frontend-search'
    ),
)
