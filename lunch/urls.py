from django.conf.urls import patterns, url
from lunch import views

urlpatterns = patterns('',
    url(r'stores/?$', views.StoreList.as_view()),
#    url(r'stores/(?P<pk>[0-9]+)/?$', views.StoreList.as_view()),
)
