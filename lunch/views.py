from rest_framework import generics, status
from rest_framework.response import Response

from lunch.models import Store
from lunch.serializers import StoreSerializer

class StoreList(generics.ListAPIView):
    '''
    List or create a Store
    '''

    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def post(self, request, format=None):
        print request.DATA
        print type(request.DATA)

        if request.DATA.get('altitude', False)\
                or request.DATA.get('longitude', False):
            alt = request.DATA.get('altitude')
            lon = request.DATA.get('longitude')

            print alt
            print lon
        else:
            print 'Nope'
        serializer = StoreSerializer()
        return Response(serializer.data, status=status.HTTP_200_OK)