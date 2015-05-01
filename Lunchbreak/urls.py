from django.conf.urls import include, patterns, url
from django.contrib import admin
from lunch import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^v1/', include('lunch.urls')),
    url(r'^v(0|[2-9]\d*)|(1\d+)/', views.WrongAPIVersionView.as_view())
)
