from django.conf.urls import patterns, url
from business import views

urlpatterns = patterns('',
    url(r'^employee/$', views.EmployeeView.as_view()),
    url(r'^employee/(?P<id>\d+)/$', views.EmployeeView.as_view()),
    url(r'^employee/reset/request/(?P<employee_id>\d+)/$', views.EmployeeRequestResetView.as_view()),

    url(r'^food/$', views.FoodListView.as_view()),
    url(r'^food/(?P<pk>\d+)/$', views.FoodRetrieveView.as_view()),
    url(r'^food/default/$', views.DefaultFoodListView.as_view()),
    url(r'^food/default/(?P<pk>\d+)/$', views.DefaultFoodRetrieveView.as_view()),

    url(r'^foodcategory/$', views.FoodCategoryListView.as_view()),

    url(r'^foodtype/$', views.FoodTypeListView.as_view()),

    url(r'^ingredient/$', views.IngredientListView.as_view()),
    url(r'^ingredient/default/$', views.DefaultIngredientListView.as_view()),

    url(r'^ingredientgroup/$', views.IngredientGroupListView.as_view()),

    url(r'^order/(?P<option>pickupTime|orderedTime)?/?$', views.OrderListView.as_view()),
    url(r'^order/(?P<pk>\d+)/$', views.OrderUpdateView.as_view()),

    url(r'^staff/$', views.StaffView.as_view()),
    url(r'^staff/(?P<id>\d+)/$', views.StaffView.as_view()),
    url(r'^staff/nearby/(?P<latitude>\d+.?\d*)/(?P<longitude>\d+.?\d*)/$', views.StaffView.as_view()),
    url(r'^staff/nearby/(?P<latitude>\d+.?\d*)/(?P<longitude>\d+.?\d*)/(?P<proximity>\d+.?\d*)/$', views.StaffView.as_view()),
    url(r'^staff/reset/request/(?P<email>.+)/$', views.StaffRequestResetView.as_view()),
    url(r'^staff/reset/(?P<email>.+)/(?P<passwordReset>.+)/$', views.StaffResetView.as_view()),

    url(r'^store/open/$', views.StoreOpenView.as_view()),
    url(r'^store/hours/$', views.OpeningHoursListView.as_view()),
    url(r'^store/holiday/$', views.HolidayPeriodListView.as_view()),

    url(r'^storecategory/$', views.StoreCategoryListView.as_view()),
)
