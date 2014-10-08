from django.conf.urls import patterns, url
from lunch import views

urlpatterns = patterns('',
    url(r'stores/(?P<latitude>.+)/(?P<longitude>.+)/$', views.StoreList.as_view()),
    url(r'stores/(?P<id>.+)/$', views.StoreList.as_view()),
#    url(r'stores/(?P<pk>[0-9]+)/?$', views.StoreList.as_view()),
)
