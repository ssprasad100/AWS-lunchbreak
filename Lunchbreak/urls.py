from django.conf.urls import include, patterns, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^aardappel/', include(admin.site.urls)),
    url(r'', include('lunch.urls')),
)
