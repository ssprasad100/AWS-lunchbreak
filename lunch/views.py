from rest_framework import generics, status
from rest_framework.response import Response

from lunch.models import Store, Food, User
from lunch.serializers import StoreSerializer, FoodSerializer, TokenSerializer, UserSerializer, UserConfirmationSerializer
from lunch.exceptions import DigitsException, InvalidRequest, DoesNotExist
from lunch.authentication import LunchbreakAuthentication
from lunch.digits import Digits


class StoreListView(generics.ListAPIView):
    '''
    List the stores.
    '''

    authentication_classes = (LunchbreakAuthentication,)
    serializer_class = StoreSerializer

    def get_queryset(self):
        proximity = self.kwargs['proximity'] if 'proximity' in self.kwargs else 5
        if 'latitude' in self.kwargs and 'longitude' in self.kwargs:
            return Store.objects.nearby(self.kwargs['latitude'], self.kwargs['longitude'], proximity)
        elif 'id' in self.kwargs:
            return Store.objects.filter(id=self.kwargs['id'])


class FoodListView(generics.ListAPIView):
    '''
    List the available food.
    '''

    authentication_classes = (LunchbreakAuthentication,)
    serializer_class = FoodSerializer

    def get_queryset(self):
        if 'store_id' in self.kwargs:
            return Food.objects.filter(store_id=self.kwargs['store_id'])
        elif 'id' in self.kwargs:
            return Food.objects.filter(id=self.kwargs['id'])


class TokenView(generics.ListCreateAPIView, generics.DestroyAPIView):
    '''
    Tokens can be created, listed (only the device names and ids) and destroyed.
    '''

    serializer_class = TokenSerializer

    def get_queryset(self):
        pass


class UserConfirmationView(generics.UpdateAPIView):
    '''
    Sign a user in and return a token.
    '''

    serializer_class = UserConfirmationSerializer

    def get_queryset(self):
        return

    def update(self, request, *args, **kwargs):
        print request.DATA
        return
        queryset = self.get_queryset()
        if not queryset:
            raise DoesNotExist('User does not exist.')

        digits = Digits()
        userId = self.kwargs['id']
        print userId


          # print 'FIRST'
        # print request.DATA
        # userSerializer = UserSerializer(data=request.DATA)
        # if userSerializer.is_valid():
        #     print 'SECOND'
        #     print request.DATA
        #     user = userSerializer.save()
        #     tokenSerializer = TokenSerializer(data=request.DATA)
        #     if tokenSerializer.is_valid():
        #         tokenSerializer.save()
        #         return Response(tokenSerializer.data)
        #     # If the token generation failed, delete the user
        #     user.delete()
        #     return Response(tokenSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(generics.CreateAPIView):
    '''
    Register a user.
    '''

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(phone=self.kwargs['phone'])

    def create(self, request, *args, **kwargs):
        userSerializer = UserSerializer(data=request.DATA)
        if userSerializer.is_valid():
            phone = request.DATA.__getitem__('phone')
            queryset = User.objects.filter(phone=phone)
            if not queryset:
                # The user isn't in the database, we want to register them.
                digits = Digits()
                try:
                    content = digits.register(phone)
                    userSerializer.save()
                    return Response(userSerializer.data)
                except:  # Will go here if the user is in the Digits database
                    try:
                        content = digits.signin(phone)
                        userSerializer.save()
                        data = {
                            'userId': content['login_verification_user_id'],
                            'requestId': content['login_verification_request_id']
                        }
                        return Response(data)
                    except Exception as e:
                        raise e
                        raise DigitsException()
            # (ELSE) The user is in the database -> Invalid Request
            raise InvalidRequest('User already exists, please use the signin API request instead.')
        # Invalid
        raise InvalidRequest()
