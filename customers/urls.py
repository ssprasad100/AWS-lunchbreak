from django.conf.urls import patterns, url
from customers import views

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
    # Version 3 deprecated, use /store/{id}/food
    url(
        r'^food/store/(?P<store_id>\d+)/?$',
        views.FoodListView.as_view()
    ),

    url(
        r'^foodcategory/(?P<pk>\d+)/?$',
        views.FoodCategoryRetrieveView.as_view()
    ),

    # Version 3 deprecated, use /user/order/ instead
    url(
        r'^order/?$',
        views.OrderView.as_view(),
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

    # Deprecated version 3, user /store/{id}/{option}/
    url(
        r'^store/(?P<option>heart|unheart)/(?P<pk>\d+)/?$',
        views.StoreHeartView.as_view()
    ),
    # Deprecated version 3, use /store/{id}/holidayperiods
    url(
        r'^store/holiday/(?P<store_id>\d+)/?$',
        views.HolidayPeriodListView.as_view()
    ),
    # Deprecated version 3, use /store/{id}/openinghours
    url(
        r'^store/hours/(?P<store_id>\d+)/?$',
        views.OpeningHoursListView.as_view()
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
    # Deprecated version 3, use /store/{id}/hours
    url(
        r'^store/open'
        r'/(?P<store_id>\d+)/?$',
        views.StoreHoursView.as_view()
    ),
    url(
        r'^store/recent/?$',
        views.StoreMultiView.as_view()
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
        r'^user/?$',
        views.UserView.as_view()
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
