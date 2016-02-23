from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'',
        views.IndexPage.as_view()
    ),
)
