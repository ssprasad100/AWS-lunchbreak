from django.conf.urls import patterns, url
from customers import views

urlpatterns = patterns('',
    url(r'^food/(?P<pk>\d+)/$', views.FoodRetrieveView.as_view()),
    url(r'^food/store/(?P<store_id>\d+)/$', views.FoodListView.as_view()),
    url(r'^food/category/(?P<foodcategory_id>\d+)/$', views.FoodListView.as_view()),

    url(r'^foodcategory/(?P<pk>\d+)/$', views.FoodCategoryRetrieveView.as_view()),

    url(r'^order/$', views.OrderView.as_view()),
    url(r'^order/(?P<pk>\d+)/$', views.OrderRetrieveView.as_view()),
    url(r'^order/price/$', views.OrderPriceView.as_view()),

    url(r'^store/(?P<pk>\d+)/$', views.StoreHeartView.as_view()),
    url(r'^store/(?P<store_id>\d+)/foodcategories/$', views.FoodCategoryListView.as_view()),
    url(r'^store/(?P<option>heart|unheart)/(?P<pk>\d+)/$', views.StoreHeartView.as_view()),
    url(r'^store/holiday/(?P<store_id>\d+)/$', views.HolidayPeriodListView.as_view()),
    url(r'^store/hours/(?P<store_id>\d+)/$', views.OpeningHoursListView.as_view()),
    url(r'^store/nearby/(?P<latitude>-?\d+.?\d*)/(?P<longitude>-?\d+.?\d*)/$', views.StoreMultiView.as_view()),
    url(r'^store/nearby/(?P<latitude>-?\d+.?\d*)/(?P<longitude>-?\d+.?\d*)/(?P<proximity>\d+.?\d*)/$', views.StoreMultiView.as_view()),
    url(r'^store/open/(?P<store_id>\d+)/$', views.StoreOpenView.as_view()),
    url(r'^store/recent/$', views.StoreMultiView.as_view()),
    url(r'^storecategory/$', views.StoreCategoryListView.as_view()),

    url(r'^token/$', views.UserTokenView.as_view()),

    url(r'^user/$', views.UserView.as_view()),
    url(r'^user/register/$', views.UserRegisterView.as_view(), name='user-registration'),
    url(r'^user/login/$', views.UserLoginView.as_view(), name='user-login')
)
