from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(
        r'^redirectflow/create/?$',
        views.RedirectFlowCreateView.as_view(),
        name='gocardless-redirectflow-create'
    ),
    url(
        r'^redirectflow/success/?$',
        views.RedirectFlowSuccessView.as_view(),
        name='gocardless-redirectflow-success'
    ),

    url(
        r'^webhook/?$',
        views.WebhookView.as_view(),
        name='gocardless-webhook'
    ),

    url(
        r'^redirect/?$',
        views.OAuthRedirectView.as_view(),
        name='gocardless-redirect'
    ),
)
