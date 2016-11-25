from django.conf.urls import patterns, url
from lunch import views as lunch_views
from lunch.views import (StoreHolidayPeriodViewSet, StoreOpeningPeriodViewSet,
                         StorePeriodsViewSet)
from rest_framework.routers import SimpleRouter
from rest_framework_extensions.routers import ExtendedSimpleRouter

from .. import views

router_simple = SimpleRouter()
router_simple.register(
    r'food',
    views.FoodViewSet,
    base_name='customers-food'
)
router_simple.register(
    r'order',
    views.OrderViewSet,
    base_name='customers-order'
)
router_simple.register(
    r'user',
    views.UserViewSet,
    base_name='customers-user'
)
router_simple.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
)

router_extended = ExtendedSimpleRouter()
router_extended.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
).register(
    r'food',
    views.StoreFoodViewSet,
    base_name='customers-store-food',
    parents_query_lookups=[
        'pk'
    ]
)
router_extended.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
).register(
    r'menu',
    views.StoreMenuViewSet,
    base_name='customers-store-menu',
    parents_query_lookups=[
        'pk'
    ]
)
router_extended.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
).register(
    r'openingperiods',
    StoreOpeningPeriodViewSet,
    base_name='customers-store-openingperiods',
    parents_query_lookups=[
        'pk'
    ]
)
router_extended.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
).register(
    r'holidayperiods',
    StoreHolidayPeriodViewSet,
    base_name='customers-store-holidayperiods',
    parents_query_lookups=[
        'pk'
    ]
)
router_extended.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
).register(
    r'periods',
    StorePeriodsViewSet,
    base_name='customers-store-periods',
    parents_query_lookups=[
        'pk'
    ]
)
router_extended.register(
    r'store',
    views.StoreViewSet,
    base_name='customers-store'
).register(
    r'groups',
    views.StoreGroupViewSet,
    base_name='customers-store-groups',
    parents_query_lookups=[
        'pk'
    ]
)

urlpatterns = patterns(
    '',
    url(
        r'^food/menu/(?P<menu_id>\d+)/?$',
        views.FoodViewSet.as_view(
            {
                'get': 'list'
            }
        ),
        name='customer-food-menu-list'
    ),

    url(
        r'^menu/(?P<pk>\d+)/?$',
        views.MenuRetrieveView.as_view()
    ),

    url(
        r'^store/(?P<store_id>\d+)/header/(?P<width>\d+)/(?P<height>\d+)/?$',
        lunch_views.StoreHeaderView.as_view(),
        name='customers-store-header'
    ),
    url(
        r'^store/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'list'
            }
        )
    ),
    url(
        r'^store/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)'
        r'/(?P<proximity>\d+.?\d*)/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'list'
            }
        )
    ),
    url(
        r'^store/recent/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'list'
            }
        ),
        {
            'recent': True
        }
    ),
    url(
        r'^storecategory/?$',
        views.StoreCategoryListView.as_view()
    ),
) + router_simple.urls + router_extended.urls
