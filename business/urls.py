from django.conf.urls import patterns, url
from business import views

urlpatterns = patterns('',
    url(r'^employee/$', views.EmployeeView.as_view()),
    url(r'^employee/reset/request/(?P<employee_id>\d+)/$', views.EmployeeRequestResetView.as_view()),

    url(r'^food/(?P<datetime>[0-3][0-9]-[0-1][0-9]-20[0-9][0-9]-[0-2][0-9]-[0-5][0-9]-[0-5][0-9])?/?$', views.FoodView.as_view()),
    url(r'^food/(?P<pk>\d+)/$', views.FoodSingleView.as_view()),
    url(r'^food/default/$', views.DefaultFoodListView.as_view()),
    url(r'^food/default/(?P<pk>\d+)/$', views.DefaultFoodSingleView.as_view()),

    url(r'^foodcategory/$', views.FoodCategoryMultiView.as_view()),
    url(r'^foodcategory/(?P<pk>\d+)/$', views.FoodCategorySingleView.as_view()),

    url(r'^foodtype/$', views.FoodTypeListView.as_view()),

    url(r'^ingredient/(?P<datetime>[0-3][0-9]-[0-1][0-9]-20[0-9][0-9]-[0-2][0-9]-[0-5][0-9]-[0-5][0-9])?/?$', views.IngredientMultiView.as_view()),
    url(r'^ingredient/(?P<pk>\d+)/$', views.IngredientSingleView.as_view()),
    url(r'^ingredient/default/$', views.DefaultIngredientListView.as_view()),

    url(r'^ingredientgroup/$', views.IngredientGroupMultiView.as_view()),
    url(r'^ingredientgroup/(?P<pk>\d+)/$', views.IngredientGroupSingleView.as_view()),
    url(r'^ingredientgroup/default/$', views.DefaultIngredientGroupMultiView.as_view()),
    url(r'^ingredientgroup/default/(?P<foodType>\d+)/$', views.DefaultIngredientGroupMultiView.as_view()),

    url(r'^order/(?P<option>pickupTime|orderedTime)?/?(?P<datetime>[0-3][0-9]-[0-1][0-9]-20[0-9][0-9]-[0-2][0-9]-[0-5][0-9]-[0-5][0-9])?/?$', views.OrderListView.as_view()),
    url(r'^order/(?P<pk>\d+)/$', views.OrderUpdateView.as_view()),

    url(r'^staff/$', views.StaffView.as_view()),
    url(r'^staff/nearby/(?P<latitude>-?\d+.?\d*)/(?P<longitude>-?\d+.?\d*)/$', views.StaffView.as_view()),
    url(r'^staff/nearby/(?P<latitude>-?\d+.?\d*)/(?P<longitude>-?\d+.?\d*)/(?P<proximity>\d+.?\d*)/$', views.StaffView.as_view()),
    url(r'^staff/reset/request/(?P<email>.+)/$', views.StaffRequestResetView.as_view()),
    url(r'^staff/reset/(?P<email>.+)/(?P<passwordReset>.+)/$', views.StaffResetView.as_view()),

    url(r'^store/open/$', views.StoreOpenView.as_view()),
    url(r'^store/hours/$', views.OpeningHoursListView.as_view()),
    url(r'^store/holiday/$', views.HolidayPeriodListView.as_view()),

    url(r'^storecategory/$', views.StoreCategoryListView.as_view()),
)
