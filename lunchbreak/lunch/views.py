import datetime

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HolidayPeriod, OpeningHours, StoreCategory
from .responses import WrongAPIVersion
from .serializers import (HolidayPeriodSerializer, OpeningHoursSerializer,
                          StoreCategorySerializer)


class OpeningHoursListViewBase(generics.ListAPIView):
    serializer_class = OpeningHoursSerializer
    pagination_class = None

    def get_store_id(self):
        raise NotImplementedError('get_store_id() needs to return the id of the store.')

    def get_queryset(self):
        return self._get_queryset(self.get_store_id())

    @staticmethod
    def _get_queryset(store_id):
        return OpeningHours.objects.filter(
            store_id=store_id
        ).order_by(
            'day',
            'opening'
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
    serializer_class = OpeningHoursSerializer
    pagination_class = None

    def get_store_id(self):
        raise NotImplementedError('get_store_id() needs to return the id of the store.')

    def get(self, request, pk=None):
        store_id = self.get_store_id()
        openinghours = OpeningHoursSerializer(
            OpeningHoursListViewBase._get_queryset(store_id),
            many=True
        )
        holidayperiods = HolidayPeriodSerializer(
            HolidayPeriodListViewBase._get_queryset(store_id),
            many=True
        )

        data = {
            'openinghours': openinghours.data,
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
