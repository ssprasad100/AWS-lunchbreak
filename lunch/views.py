from rest_framework import generics

from lunch.models import Store
from lunch.serializers import StoreSerializer


class StoreList(generics.ListAPIView):
    '''
    List or create a Store
    '''

    serializer_class = StoreSerializer

    def get_queryset(self):
        if 'latitude' in self.kwargs is not None and 'longitude' in self.kwargs is not None:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], 5)
        if 'id' in self.kwargs is not None:
            return Store.objects.filter(id=self.kwargs['id'])
        return Store.objects.all()
