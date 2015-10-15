from business import views
from business.authentication import EmployeeAuthentication, StaffAuthentication
from business.models import Employee, EmployeeToken, Staff, StaffToken
from business.serializers import (EmployeePasswordSerializer,
                                  StaffPasswordSerializer)
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(
        r'^employee/?$',
        views.EmployeeView.as_view()
    ),
    url(
        r'^employee/reset/?$',
        views.PasswordResetView.as_view(),
        {
            'model': Employee,
            'tokenModel': EmployeeToken,
            'serializerClass': EmployeePasswordSerializer,
            'employee': True
        }
    ),
    url(
        r'^employee/reset/request/?$',
        views.ResetRequestView.as_view(),
        {
            'authentication': EmployeeAuthentication
        }
    ),

    url(
        r'^food/(?P<since>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.FoodView.as_view()
    ),
    url(
        r'^food/(?P<pk>\d+)/?$',
        views.FoodSingleView.as_view()
    ),
    url(
        r'^food/popular/(?P<frm>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/(?P<to>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.FoodPopularView.as_view()
    ),

    url(
        r'^foodcategory/?$',
        views.FoodCategoryMultiView.as_view()
    ),
    url(
        r'^foodcategory/(?P<pk>\d+)/?$',
        views.FoodCategorySingleView.as_view()
    ),

    url(
        r'^foodtype/?$',
        views.FoodTypeListView.as_view()
    ),

    url(
        r'^ingredient/(?P<datetime>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.IngredientMultiView.as_view()
    ),
    url(
        r'^ingredient/(?P<pk>\d+)/?$',
        views.IngredientSingleView.as_view()
    ),

    url(
        r'^ingredientgroup/?$',
        views.IngredientGroupMultiView.as_view()
    ),
    url(
        r'^ingredientgroup/(?P<pk>\d+)/?$',
        views.IngredientGroupSingleView.as_view()
    ),

    url(
        r'^order/(?P<option>pickupTime|orderedTime)?/?(?P<datetime>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.OrderListView.as_view()
    ),
    url(
        r'^order/(?P<pk>\d+)/?$',
        views.OrderUpdateView.as_view()
    ),
    url(
        r'^order/spread/(?P<unit>hour|weekday|day|month|quarter|year)/(?P<frm>\d{8}T\d{6})/(?P<to>\d{8}T\d{6})?/?$',
        views.OrderSpreadView.as_view({'get': 'list'})
    ),

    url(
        r'^quantity/?$',
        views.QuantityMultiView.as_view()
    ),
    url(
        r'^quantity/(?P<pk>\d+)/?$',
        views.QuantitySingleView.as_view()
    ),

    url(
        r'^staff/?$',
        views.StaffMultiView.as_view()
    ),
    url(
        r'^staff/(?P<pk>\d+)/?$',
        views.StaffSingleView.as_view()
    ),
    url(
        r'^staff/nearby/(?P<latitude>-?\d+.?\d*)/(?P<longitude>-?\d+.?\d*)/?$',
        views.StaffMultiView.as_view()
    ),
    url(
        r'^staff/nearby/(?P<latitude>-?\d+.?\d*)/(?P<longitude>-?\d+.?\d*)/(?P<proximity>\d+.?\d*)/?$',
        views.StaffMultiView.as_view()
    ),
    url(
        r'^staff/reset/request/?$',
        views.ResetRequestView.as_view(),
        {
            'authentication': StaffAuthentication
        }
    ),
    url(
        r'^staff/reset/?$',
        views.PasswordResetView.as_view(),
        {
            'model': Staff,
            'tokenModel': StaffToken,
            'serializerClass': StaffPasswordSerializer
        }
    ),

    url(
        r'^store/?$',
        views.StoreSingleView.as_view()
    ),
    url(
        r'^store/open/?$',
        views.StoreOpenView.as_view()
    ),
    url(
        r'^store/hours/?$',
        views.OpeningHoursListView.as_view()
    ),
    url(
        r'^store/holiday/?$',
        views.HolidayPeriodListView.as_view()
    ),

    url(
        r'^storecategory/?$',
        views.StoreCategoryListView.as_view()
    ),
)
