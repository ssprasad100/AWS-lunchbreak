from django.conf.urls import patterns, url
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
(
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
)
(
    router_extended.register(
        r'store',
        views.StoreViewSet,
        base_name='customers-store'
    ).register(
        r'foodcategory',
        views.StoreFoodCategoryViewSet,
        base_name='customers-store-foodcategory',
        parents_query_lookups=[
            'pk'
        ]
    )
)

urlpatterns = router_simple.urls + router_extended.urls + patterns(
    '',
    url(
        r'^food/foodcategory/(?P<foodcategory_id>\d+)/?$',
        views.FoodViewSet.as_view(
            {
                'get': 'list'
            }
        ),
        name='customer-food-foodcategory-list'
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
        r'^reservation/?$',
        views.ReservationMultiView.as_view(),
        name='customers-user-reservation'
    ),
    url(
        r'^reservation/(?P<pk>\d+)/?$',
        views.ReservationSingleView.as_view(),
        name='customers-reservation'
    ),

    url(
        r'^store/(?P<store_id>\d+)/header/(?P<width>\d+)/(?P<height>\d+)/?$',
        views.StoreHeaderView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/holidayperiods/?$',
        views.HolidayPeriodListView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/periods/?$',
        views.StorePeriodsView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/openingperiods/?$',
        views.OpeningPeriodListView.as_view()
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
)
