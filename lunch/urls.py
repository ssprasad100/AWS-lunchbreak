from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'^customers/', include('customers.urls')),
)
