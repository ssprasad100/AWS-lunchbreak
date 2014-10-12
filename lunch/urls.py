from django.conf.urls import patterns, url
from lunch import views

urlpatterns = patterns('',
    url(r'stores/(?P<latitude>\d+)/(?P<longitude>\d+)/(?P<proximity>\d+)/$', views.StoreListView.as_view()),
    url(r'stores/(?P<latitude>.+)/(?P<longitude>.+)/$', views.StoreListView.as_view()),
    url(r'stores/(?P<id>.+)/$', views.StoreListView.as_view()),
    url(r'stores/?$', views.StoreCreateView.as_view()),

    url(r'food/store/(?P<store_id>.+)/$', views.FoodListView.as_view()),
    url(r'food/(?P<id>.+)/$', views.FoodListView.as_view()),
    url(r'food/?$', views.FoodCreateView.as_view()),
)
