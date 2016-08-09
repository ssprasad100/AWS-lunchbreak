from django.conf.urls import patterns, url
from rest_framework.routers import SimpleRouter

from .. import views
from ..authentication import EmployeeAuthentication, StaffAuthentication
from ..models import Employee, EmployeeToken, Staff, StaffToken
from ..serializers import EmployeePasswordSerializer, StaffPasswordSerializer

router = SimpleRouter()
router.register(r'food', views.FoodViewSet, base_name='business-food')

urlpatterns = patterns(
    '',
    url(
        r'^employee/?$',
        views.EmployeeView.as_view()
    ),
    url(
        r'^employee/reset/?$',
        views.PasswordResetView.as_view(),
        {
            'model': Employee,
            'token_model': EmployeeToken,
            'serializer_class': EmployeePasswordSerializer,
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
        r'^menu/?$',
        views.MenuView.as_view()
    ),
    url(
        r'^menu/(?P<pk>\d+)/?$',
        views.MenuDetailView.as_view()
    ),

    url(
        r'^foodtype/?$',
        views.FoodTypeView.as_view()
    ),

    url(
        r'^ingredient/?$',
        views.IngredientView.as_view()
    ),
    url(
        r'^ingredient/(?P<pk>\d+)/?$',
        views.IngredientDetailView.as_view()
    ),

    url(
        r'^ingredientgroup/?$',
        views.IngredientGroupView.as_view()
    ),
    url(
        r'^ingredientgroup/(?P<pk>\d+)/?$',
        views.IngredientGroupDetailView.as_view()
    ),

    url(
        r'^order/?$',
        views.OrderView.as_view()
    ),
    url(
        r'^order/(?P<pk>\d+)/?$',
        views.OrderDetailView.as_view()
    ),
    url(
        r'^order/spread/?$',
        views.OrderSpreadView.as_view(
            {
                'get': 'list'
            }
        )
    ),

    url(
        r'^quantity/?$',
        views.QuantityView.as_view()
    ),
    url(
        r'^quantity/(?P<pk>\d+)/?$',
        views.QuantityDetailView.as_view()
    ),

    url(
        r'^reservation/?$',
        views.ReservationView.as_view()
    ),
    url(
        r'^reservation/(?P<pk>\d+)/?$',
        views.ReservationDetailView.as_view()
    ),

    url(
        r'^staff/?$',
        views.StaffView.as_view()
    ),
    url(
        r'^staff/(?P<pk>\d+)/?$',
        views.StaffDetailView.as_view()
    ),
    url(
        r'^staff/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)/?$',
        views.StaffView.as_view()
    ),
    url(
        r'^staff/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)'
        r'/(?P<proximity>\d+.?\d*)/?$',
        views.StaffView.as_view()
    ),
    url(
        r'^staff/reset/?$',
        views.PasswordResetView.as_view(),
        {
            'model': Staff,
            'token_model': StaffToken,
            'serializer_class': StaffPasswordSerializer
        }
    ),
    url(
        r'^staff/reset/request/?$',
        views.ResetRequestView.as_view(),
        {
            'authentication': StaffAuthentication
        }
    ),

    url(
        r'^store/?$',
        views.StoreDetailView.as_view()
    ),
    url(
        r'^store/openingperiods/?$',
        views.OpeningPeriodView.as_view()
    ),
    url(
        r'^store/holidayperiods/?$',
        views.HolidayPeriodView.as_view()
    ),
    url(
        r'^store/periods/?$',
        views.StoreOpenView.as_view()
    ),

    url(
        r'^storecategory/?$',
        views.StoreCategoryView.as_view()
    ),
) + router.urls
