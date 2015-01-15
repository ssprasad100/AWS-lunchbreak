from django.conf.urls import patterns, url
from lunch import views

urlpatterns = patterns('',
	url(r'stores/nearby/(?P<latitude>.+)/(?P<longitude>.+)/(?P<proximity>.+)/$', views.StoreListView.as_view()),
	url(r'stores/nearby/(?P<latitude>.+)/(?P<longitude>.+)/$', views.StoreListView.as_view()),
	url(r'stores/(?P<id>.+)/$', views.StoreListView.as_view()),

	url(r'food/store/(?P<store_id>.+)/$', views.FoodListView.as_view()),
	url(r'food/(?P<id>.+)/$', views.FoodListView.as_view()),

	url(r'order/price/$', views.OrderPriceView.as_view()),
	url(r'order/paid/(?P<id>.+)/$', views.OrderView.as_view()),
	url(r'order/update/(?P<id>.+)/(?P<status>.+)/$', views.OrderView.as_view()),
	url(r'order/(?P<id>.+)/$', views.OrderView.as_view()),
	url(r'order/$', views.OrderView.as_view()),

	url(r'token/$', views.TokenView.as_view()),

	url(r'user/$', views.UserView.as_view())
)
