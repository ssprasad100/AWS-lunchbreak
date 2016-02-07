import datetime

from django.utils import timezone
from lunch.models import HolidayPeriod, OpeningHours, StoreCategory
from lunch.responses import WrongAPIVersion
from lunch.serializers import (HolidayPeriodSerializer, OpeningHoursSerializer,
                               StoreCategorySerializer)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


def getOpeningHours(storeId):
    return OpeningHours.objects.filter(store_id=storeId).order_by('day', 'opening')


def getHolidayPeriods(storeId):
    return HolidayPeriod.objects.filter(store_id=storeId, start__lte=timezone.now() + datetime.timedelta(days=7), end__gte=timezone.now())


def getOpeningAndHoliday(storeId):
    '''
    Return both the the opening hours and holiday periods as a Response.
    '''
    openingHours = OpeningHoursSerializer(getOpeningHours(storeId), many=True)
    holidayPeriods = HolidayPeriodSerializer(getHolidayPeriods(storeId), many=True)

    data = {
        'openingHours': openingHours.data,
        'holidayPeriods': holidayPeriods.data
    }

    return Response(data=data, status=status.HTTP_200_OK)


class StoreCategoryListViewBase(generics.ListAPIView):
    '''
    List all of the store categories.
    '''

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
