import datetime

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from Lunchbreak.views import TargettedViewSet
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.mixins import NestedViewSetMixin
from sendfile import sendfile

from .exceptions import UnsupportedAPIVersion
from .models import HolidayPeriod, OpeningPeriod, Store, StoreCategory
from .renderers import JPEGRenderer
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


class StoreHeaderView(APIView):

    renderer_classes = (JPEGRenderer,)

    def get(self, request, store_id, width=None, height=None):
        store = get_object_or_404(Store, id=store_id)

        width = width if width is not None else request.query_params.get('width')
        height = height if height is not None else request.query_params.get('height')

        if height is None or width is None:
            raise Http404()

        if not hasattr(store, 'header'):
            raise Http404('That store does not have a header.')

        image = store.header.retrieve_from_source(
            'original',
            int(width),
            int(height)
        )
        try:
            return sendfile(request, image.path)
        except FileNotFoundError:
            raise Http404('File was not found.')


class StoreCategoryListViewBase(generics.ListAPIView):

    """
    List all of the store categories.
    """

    serializer_class = StoreCategorySerializer
    pagination_class = None
    queryset = StoreCategory.objects.all()


class WrongAPIVersionView(APIView):

    def get(self, request, *args, **kwargs):
        return UnsupportedAPIVersion().response

    def post(self, request, *args, **kwargs):
        return UnsupportedAPIVersion().response

    def patch(self, request, *args, **kwargs):
        return UnsupportedAPIVersion().response

    def delete(self, request, *args, **kwargs):
        return UnsupportedAPIVersion().response

    def put(self, request, *args, **kwargs):
        return UnsupportedAPIVersion().response
