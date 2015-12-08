from django.conf.urls import patterns, url
from django_gocardless import views

urlpatterns = patterns(
    '',
    url(
        r'^redirectflow/create/?$',
        views.RedirectFlowCreateView.as_view(),
        name='gocardless_redirectflow_create'
    ),
    url(
        r'^redirectflow/success/?$',
        views.RedirectFlowSuccessView.as_view(),
        name='gocardless_redirectflow_success'
    ),
)
