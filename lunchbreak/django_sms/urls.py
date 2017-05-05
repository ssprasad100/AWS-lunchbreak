from django.conf.urls import url

from . import views

app_name = 'django_sms'

urlpatterns = [
    url(
        r'^plivo/?$',
        views.PlivoWebhookView.as_view(),
        name='plivo'
    ),
    url(
        r'^twilio/?$',
        views.TwilioWebhookView.as_view(),
        name='twilio'
    ),
]
