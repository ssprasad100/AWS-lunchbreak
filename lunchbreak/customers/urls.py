from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter

from . import views

# router = DefaultRouter()
# router.register(r'invite', views.InviteViewSet)
urlpatterns = patterns(
    '',
    url(
        r'^food/(?P<pk>\d+)/?$',
        views.FoodRetrieveView.as_view()
    ),
    url(
        r'^food/category/(?P<foodcategory_id>\d+)/?$',
        views.FoodListView.as_view()
    ),

    url(
        r'^foodcategory/(?P<pk>\d+)/?$',
        views.FoodCategoryRetrieveView.as_view()
    ),

    url(
        r'^group/?$',
        views.GroupView.as_view()
    ),

    url(
        r'^invite/?$',
        views.InviteMultiView.as_view()
    ),
    url(
        r'^invite/(?P<pk>\d+)/?$',
        views.InviteSingleView.as_view()
    ),

    url(
        r'^order/(?P<pk>\d+)/?$',
        views.OrderRetrieveView.as_view()
    ),
    url(
        r'^order/price/?$',
        views.OrderPriceView.as_view()
    ),

    url(
        r'^reservation/(?P<pk>\d+)/?$',
        views.ReservationSingleView.as_view(),
        name='reservation'
    ),

    url(
        r'^store/?$',
        views.StoreMultiView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/?$',
        views.StoreHeartView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/(?P<option>heart|unheart)/?$',
        views.StoreHeartView.as_view(), name='store-heart'
    ),
    url(
        r'^store/(?P<store_id>\d+)/food/?$',
        views.FoodListView.as_view()
    ),
    url(
        r'^store/(?P<store_id>\d+)/foodcategories/?$',
        views.FoodCategoryListView.as_view()
    ),
    url(
        r'^store/(?P<store_id>\d+)/header/(?P<width>\d+)/(?P<height>\d+)/?$',
        views.StoreHeaderView.as_view()
    ),
    url(
        r'^store/(?P<store_id>\d+)/holidayperiods/?$',
        views.HolidayPeriodListView.as_view()
    ),
    url(
        r'^store/(?P<store_id>\d+)/hours/?$',
        views.StoreHoursView.as_view()
    ),
    url(
        r'^store/(?P<store_id>\d+)/openinghours/?$',
        views.OpeningHoursListView.as_view()
    ),
    url(
        r'^store/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)/?$',
        views.StoreMultiView.as_view()
    ),
    url(
        r'^store/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)'
        r'/(?P<proximity>\d+.?\d*)/?$',
        views.StoreMultiView.as_view()
    ),
    url(
        r'^store/recent/?$',
        views.StoreMultiView.as_view(),
        {
            'recent': True
        }
    ),
    url(
        r'^storecategory/?$',
        views.StoreCategoryListView.as_view()
    ),

    url(
        r'^token/?$',
        views.UserTokenView.as_view()
    ),

    url(
        r'^user/token/?$',
        views.UserTokenUpdateView.as_view(),
        name='user-token'
    ),
    url(
        r'^user/register/?$',
        views.UserRegisterView.as_view(),
        name='user-registration'
    ),
    url(
        r'^user/login/?$',
        views.UserLoginView.as_view(),
        name='user-login'
    ),
    url(
        r'^user/reservation/?$',
        views.ReservationMultiView.as_view(),
        name='user-reservation'
    ),
    url(
        r'^user/order(/(?P<pay>pay))?/?$',
        views.OrderView.as_view(),
        name='order'
    ),
)
