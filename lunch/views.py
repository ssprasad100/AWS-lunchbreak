from rest_framework import generics
from rest_framework.exceptions import APIException

import requests

from lunch.models import Store
from lunch.serializers import StoreSerializer


class StoreList(generics.ListCreateAPIView):
    '''
    List or create a Store
    '''

    serializer_class = StoreSerializer
    GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    GEOCODING_KEY = 'AIzaSyD7jRgPzUxQ4fdghdwoyTnD5hB6EOtpDhE'
    ADDRESS_FORMAT = '%s,+%s,+%s+%s,+%s+%s'

    def get_queryset(self):
        if 'latitude' in self.kwargs is not None and 'longitude' in self.kwargs is not None:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], 5)
        if 'id' in self.kwargs is not None:
            return Store.objects.filter(id=self.kwargs['id'])
        return Store.objects.all()

    def post(self, request):
        country = request.DATA.get('country')
        province = request.DATA.get('province')
        city = request.DATA.get('city')
        code = request.DATA.get('code')
        street = request.DATA.get('street')
        number = request.DATA.get('number')

        if not country or not province or not city or not code or not street or not number:
            raise APIException('The full address needs to be given.')

        address = self.ADDRESS_FORMAT % (country, province, street, number, code, city,)
        response = requests.get(self.GEOCODING_URL, params={'address': address, 'key': self.GEOCODING_KEY})
        result = response.json()

        if not result['results']:
            raise APIException('Address not found.')

        latitude = result['results'][0]['geometry']['location']['lat']
        longitude = result['results'][0]['geometry']['location']['lng']

        request.DATA.appendlist('latitude', latitude)
        request.DATA.appendlist('longitude', longitude)

        return super(StoreList, self).post(request)
