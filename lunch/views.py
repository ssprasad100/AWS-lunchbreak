import datetime

from django.utils import timezone
from lunch.models import HolidayPeriod, OpeningHours
from lunch.serializers import HolidayPeriodSerializer, OpeningHoursSerializer
from rest_framework import status
from rest_framework.response import Response


def getOpeningHours(storeId):
    return OpeningHours.objects.filter(store_id=storeId).order_by('day', 'opening')


def getHolidayPeriods(storeId):
    return HolidayPeriod.objects.filter(store_id=storeId, start__lte=timezone.now() + datetime.timedelta(days=7), end__gte=timezone.now())


def getOpeningAndHoliday(storeId):
    openingHours = OpeningHoursSerializer(getOpeningHours(storeId), many=True)
    holidayPeriods = HolidayPeriodSerializer(getHolidayPeriods(storeId), many=True)

    data = {
        'openingHours': openingHours.data,
        'holidayPeriods': holidayPeriods.data
    }

    return Response(data=data, status=status.HTTP_200_OK)
