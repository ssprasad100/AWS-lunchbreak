from django.conf.urls import include, patterns, url
from django.contrib import admin
from lunch import views

urlpatterns = patterns('',
    url(r'^aardappel/', include(admin.site.urls)),
    url(r'^v1/', include('lunch.urls')),
    url(r'^v0/', views.WrongAPIVersionView.as_view())
)
