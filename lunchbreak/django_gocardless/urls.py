from django.conf.urls import url

from . import views

app_name = 'gocardless'
urlpatterns = [
    url(
        r'^redirectflow/create/?$',
        views.RedirectFlowCreateView.as_view(),
        name='redirectflow-create'
    ),
    url(
        r'^redirectflow/success/?$',
        views.RedirectFlowSuccessView.as_view(),
        name='redirectflow-success'
    ),

    url(
        r'^webhook/?$',
        views.WebhookView.as_view(),
        name='webhook'
    ),
    url(
        r'^webhook/app/?$',
        views.WebhookView.as_view(),
        name='webhook-app',
        kwargs={
            'is_app': True
        }
    ),

    url(
        r'^redirect/?$',
        views.OAuthRedirectView.as_view(),
        name='redirect'
    ),
]
