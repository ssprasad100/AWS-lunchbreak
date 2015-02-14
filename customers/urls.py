from django.conf.urls import patterns, url
from customers import views

urlpatterns = patterns('',
    url(r'stores/nearby/(?P<latitude>.+)/(?P<longitude>.+)/(?P<proximity>.+)/$', views.StoreListView.as_view(), name='store_nearby_proximity'),
    url(r'stores/nearby/(?P<latitude>.+)/(?P<longitude>.+)/$', views.StoreListView.as_view(), name='store_nearby'),
    url(r'stores/hours/(?P<store_id>.+)/$', views.OpeningHoursListView.as_view(), name='store_hours'),
    url(r'stores/holiday/(?P<store_id>.+)/$', views.HolidayPeriodListView.as_view(), name='store_holiday'),
    url(r'stores/(?P<id>.+)/$', views.StoreListView.as_view(), name='store_specific'),

    url(r'food/store/(?P<store_id>.+)/$', views.FoodListView.as_view(), name='food_store'),
    url(r'food/(?P<id>.+)/$', views.FoodListView.as_view(), name='food_specific'),

    url(r'order/price/$', views.OrderPriceView.as_view(), name='order_price'),
    url(r'order/paid/(?P<id>.+)/$', views.OrderView.as_view(), name='order_paid'),
    url(r'order/update/(?P<id>.+)/(?P<status>.+)/$', views.OrderView.as_view(), name='order_update'),
    url(r'order/(?P<id>.+)/$', views.OrderView.as_view(), name='order_specific'),
    url(r'order/$', views.OrderView.as_view(), name='order'),

    url(r'token/$', views.TokenView.as_view(), name='token'),

    url(r'user/$', views.UserView.as_view(), name='user')
)
