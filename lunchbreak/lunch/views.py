import datetime

from django.utils import timezone
from Lunchbreak.views import TargettedViewSet
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import HolidayPeriod, OpeningPeriod, StoreCategory
from .responses import WrongAPIVersion
from .serializers import (HolidayPeriodSerializer, OpeningPeriodSerializer,
                          StoreCategorySerializer)


class StoreOpeningPeriodViewSet(TargettedViewSet,
                                NestedViewSetMixin,
                                mixins.ListModelMixin):

    serializer_class = OpeningPeriodSerializer
    pagination_class = None

    @property
    def queryset(self):
        return self._get_queryset(
            parent_pk=self.kwargs['parent_lookup_pk']
        )

    @classmethod
    def _get_queryset(cls, parent_pk):
        return OpeningPeriod.objects.filter(
            store_id=parent_pk
        ).order_by(
            'day',
            'time'
        )


class StoreHolidayPeriodViewSet(TargettedViewSet,
                                NestedViewSetMixin,
                                mixins.ListModelMixin):

    serializer_class = HolidayPeriodSerializer
    pagination_class = None

    @property
    def queryset(self):
        return self._get_queryset(
            parent_pk=self.kwargs['parent_lookup_pk']
        )

    @classmethod
    def _get_queryset(cls, parent_pk):
        return HolidayPeriod.objects.filter(
            store_id=parent_pk,
            start__lte=timezone.now() + datetime.timedelta(days=7),
            end__gte=timezone.now()
        )


class StorePeriodsViewSet(TargettedViewSet,
                          NestedViewSetMixin,
                          mixins.ListModelMixin):
    serializer_class = OpeningPeriodSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        openingperiods = OpeningPeriodSerializer(
            StoreOpeningPeriodViewSet._get_queryset(
                parent_pk=self.kwargs['parent_lookup_pk']
            ),
            many=True
        )
        holidayperiods = HolidayPeriodSerializer(
            StoreHolidayPeriodViewSet._get_queryset(
                parent_pk=self.kwargs['parent_lookup_pk']
            ),
            many=True
        )

        data = {
            'openingperiods': openingperiods.data,
            'holidayperiods': holidayperiods.data
        }

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )


class StoreCategoryListViewBase(generics.ListAPIView):

    """
    List all of the store categories.
    """

    serializer_class = StoreCategorySerializer
    pagination_class = None
    queryset = StoreCategory.objects.all()


class WrongAPIVersionView(APIView):

    def get(self, request, *args, **kwargs):
        return WrongAPIVersion()

    def post(self, request, *args, **kwargs):
        return WrongAPIVersion()

    def patch(self, request, *args, **kwargs):
        return WrongAPIVersion()

    def delete(self, request, *args, **kwargs):
        return WrongAPIVersion()

    def put(self, request, *args, **kwargs):
        return WrongAPIVersion()
