from django.conf.urls import url

from . import views

app_name = 'payconiq'

urlpatterns = [
    url(
        r'',
        views.WebhookView.as_view(),
        name='webhook'
    ),
]
