from django.conf.urls import patterns, url
from customers import views

urlpatterns = patterns('',
    url(r'^food/(?P<pk>\d+)/$', views.FoodRetrieveView.as_view()),
    url(r'^food/store/(?P<store_id>\d+)/$', views.FoodListView.as_view()),

    url(r'^order/$', views.OrderView.as_view()),
    url(r'^order/(?P<pk>\d+)/$', views.OrderRetrieveView.as_view()),
    url(r'^order/price/$', views.OrderPriceView.as_view()),

    url(r'^store/(?P<id>\d+)/$', views.StoreListView.as_view()),
    url(r'^store/(?P<option>heart|unheart)/(?P<store_id>\d+)/$', views.StoreHeartView.as_view()),
    url(r'^store/unheart/(?P<store_dislike>\d+)/$', views.StoreHeartView.as_view()),
    url(r'^store/holiday/(?P<store_id>\d+)/$', views.HolidayPeriodListView.as_view()),
    url(r'^store/hours/(?P<store_id>\d+)/$', views.OpeningHoursListView.as_view()),
    url(r'^store/nearby/(?P<latitude>\d+\.\d+)/(?P<longitude>\d+\.\d+)/$', views.StoreListView.as_view()),
    url(r'^store/nearby/(?P<latitude>\d+\.\d+)/(?P<longitude>\d+\.\d+)/(?P<proximity>\d+)/$', views.StoreListView.as_view()),
    url(r'^store/open/(?P<store_id>\d+)/$', views.StoreOpenView.as_view()),

    url(r'^storecategory/$', views.StoreCategoryListView.as_view()),

    url(r'^token/$', views.UserTokenView.as_view()),

    url(r'^user/$', views.UserView.as_view())
)
