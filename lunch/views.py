from rest_framework import generics
from rest_framework.exceptions import APIException

from lunch.models import Store, Food
from lunch.serializers import StoreSerializer, FoodSerializer

import requests


class StoreListView(generics.ListAPIView):
    '''
    List the stores.
    '''

    serializer_class = StoreSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs is not None and 'longitude' in self.kwargs is not None:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
        if 'id' in self.kwargs is not None:
            return Store.objects.filter(id=self.kwargs['id'])
        return Store.objects.all()


class StoreCreateView(generics.CreateAPIView, StoreListView):
    '''
    Create or list stores.
    '''
    serializer_class = StoreSerializer


class FoodListView(generics.ListAPIView):
    '''
    List the available food.
    '''

    serializer_class = FoodSerializer

    def get_queryset(self):
        if 'store_id' in self.kwargs is not None:
            return Food.objects.filter(store_id=self.kwargs['store_id'])
        if 'id' in self.kwargs is not None:
            return Food.objects.filter(id=self.kwargs['id'])
        return Food.objects.all()


class FoodCreateView(generics.CreateAPIView, FoodListView):
    '''
    Add food.
    '''

    serializer_class = FoodSerializer
    queryset = Food.objects.all()
