from django.conf.urls import patterns, url
from rest_framework.routers import SimpleRouter

from .. import views
from ..authentication import EmployeeAuthentication, StaffAuthentication
from ..models import Employee, EmployeeToken, Staff, StaffToken
from ..serializers import EmployeePasswordSerializer, StaffPasswordSerializer

router = SimpleRouter()
router.register(r'food', views.FoodViewSet, base_name='business-food')

urlpatterns = router.urls + patterns(
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
        r'^food/(?P<since>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.FoodViewSet.as_view(
            {
                'get': 'list'
            }
        )
    ),
    url(
        r'^food/popular'
        r'/(?P<frm>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?'
        r'/(?P<to>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.FoodViewSet.as_view(
            {
                'get': 'popular'
            }
        )
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
        r'^ingredient'
        r'/(?P<datetime>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
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
        r'^order'
        r'/(?P<option>pickup|placed)?'
        r'/?(?P<datetime>\d{8}T\d{6}|\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{2})?/?$',
        views.OrderListView.as_view()
    ),
    url(
        r'^order/(?P<pk>\d+)/?$',
        views.OrderUpdateView.as_view()
    ),
    url(
        r'^order/spread'
        r'/(?P<unit>hour|week|weekday|day|month|quarter|year|price)'
        r'/(?P<frm>\d{8}T\d{6})/(?P<to>\d{8}T\d{6})?/?$',
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
        r'^reservation/?$',
        views.ReservationMultiView.as_view()
    ),
    url(
        r'^reservation/(?P<pk>\d+)/?$',
        views.ReservationSingleView.as_view()
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
        r'^staff/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)/?$',
        views.StaffMultiView.as_view()
    ),
    url(
        r'^staff/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)'
        r'/(?P<proximity>\d+.?\d*)/?$',
        views.StaffMultiView.as_view()
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
        views.StoreSingleView.as_view()
    ),
    url(
        r'^store/hours/?$',
        views.OpeningPeriodListView.as_view()
    ),
    url(
        r'^store/holiday/?$',
        views.HolidayPeriodListView.as_view()
    ),
    url(
        r'^store/open/?$',
        views.StoreOpenView.as_view()
    ),

    url(
        r'^storecategory/?$',
        views.StoreCategoryListView.as_view()
    ),
)
