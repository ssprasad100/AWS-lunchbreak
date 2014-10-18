from rest_framework import generics

from lunch.models import Store, Food
from lunch.serializers import StoreSerializer, FoodSerializer


class StoreListView(generics.ListAPIView):
    '''
    List the stores.
    '''

    serializer_class = StoreSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs is not None and 'longitude' in self.kwargs is not None:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
        elif 'id' in self.kwargs is not None:
            return Store.objects.filter(id=self.kwargs['id'])


class FoodListView(generics.ListAPIView):
    '''
    List the available food.
    '''

    serializer_class = FoodSerializer

    def get_queryset(self):
        if 'store_id' in self.kwargs is not None:
            return Food.objects.filter(store_id=self.kwargs['store_id'])
        elif 'id' in self.kwargs is not None:
            return Food.objects.filter(id=self.kwargs['id'])
