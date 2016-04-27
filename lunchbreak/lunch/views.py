import datetime

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HolidayPeriod, OpeningPeriod, StoreCategory
from .responses import WrongAPIVersion
from .serializers import (HolidayPeriodSerializer, OpeningPeriodSerializer,
                          StoreCategorySerializer)


class OpeningPeriodListViewBase(generics.ListAPIView):
    serializer_class = OpeningPeriodSerializer
    pagination_class = None

    def get_store_id(self):
        raise NotImplementedError('get_store_id() needs to return the id of the store.')

    def get_queryset(self):
        return self._get_queryset(self.get_store_id())

    @staticmethod
    def _get_queryset(store_id):
        return OpeningPeriod.objects.filter(
            store_id=store_id
        ).order_by(
            'day',
            'time'
        )


class HolidayPeriodListViewBase(generics.ListAPIView):
    serializer_class = HolidayPeriodSerializer
    pagination_class = None

    def get_store_id(self):
        raise NotImplementedError('get_store_id() needs to return the id of the store.')

    def get_queryset(self):
        return self._get_queryset(self.get_store_id())

    @staticmethod
    def _get_queryset(store_id):
        return HolidayPeriod.objects.filter(
            store_id=store_id,
            start__lte=timezone.now() + datetime.timedelta(days=7),
            end__gte=timezone.now()
        )


class OpeningListViewBase(generics.ListAPIView):
    serializer_class = OpeningPeriodSerializer
    pagination_class = None

    def get_store_id(self):
        raise NotImplementedError(
            'get_store_id() needs to return the id of the store.'
        )

    def get(self, request, pk=None):
        store_id = self.get_store_id()
        OpeningPeriod = OpeningPeriodSerializer(
            OpeningPeriodListViewBase._get_queryset(store_id),
            many=True
        )
        holidayperiods = HolidayPeriodSerializer(
            HolidayPeriodListViewBase._get_queryset(store_id),
            many=True
        )

        data = {
            'openingperiods': OpeningPeriod.data,
            'holidayperiods': holidayperiods.data
        }

        return Response(data=data, status=status.HTTP_200_OK)


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
