from rest_framework import generics
from rest_framework.response import Response

from lunch.models import Store, Food, User, Token
from lunch.serializers import StoreSerializer, FoodSerializer, TokenSerializer, UserSerializer
from lunch.exceptions import DigitsException, InvalidRequest
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


class TokenView(generics.ListAPIView):
    '''
    Tokens can only be listed (for now).
    '''

    authentication_classes = (LunchbreakAuthentication,)
    serializer_class = TokenSerializer

    def get_queryset(self):
        '''
        Return all of the Tokens for the authenticated user.
        '''
        return Token.objects.filter(user=self.request.user)


class UserView(generics.CreateAPIView):

    serializer_class = UserSerializer

    # For all these methods a try-except is not needed since a DigitsException is generated
    # which will provide everything
    def register(self, digits, phone):
        try:
            digits.register(phone)
            return True
        except:
            return self.signIn(digits, phone)

    def signIn(self, digits, phone):
        content = digits.signin(phone)
        return {
            'userId': content['login_verification_user_id'],
            'requestId': content['login_verification_request_id']
        }

    def confirmRegistration(self, digits, phone, pin):
        content = digits.confirmRegistration(phone, pin)
        return content['id']

    def confirmSignin(self, digits, requestId, userId, pin):
        digits.confirmSignin(requestId, userId, pin)
        return True

    def create(self, request, *args, **kwargs):
        userSerializer = UserSerializer(data=request.data)
        if userSerializer.is_valid():
            phone = request.data.__getitem__('phone')
            print phone
            queryset = User.objects.filter(phone=phone)
            print queryset
            digits = Digits()
            if not queryset:
                print 'User is not in the database yet'
                result = self.register(digits, phone)
                if result:
                    user = User(phone=phone, name=request.data.__getitem__('name'))
                    if type(result) is dict:
                        print '    User is in the Digits Database'
                        user.userId = result['userId']
                        user.requestId = result['requestId']
                    user.save()
                    return Response()
                raise DigitsException()
            else:
                print 'User is in the database'
                pin = request.data.get('pin', False)
                user = queryset[0]
                if not pin:
                    print '    No pin was given'
                    if user.confirmed:
                        print '        User is confirmed'
                        result = self.signIn(digits, phone)
                        if result:
                            user.userId = result['userId']
                            user.requestId = result['requestId']
                            user.save()
                            return Response()
                    else:
                        print '        User is not confirmed'
                        result = self.register(digits, phone)
                        if result:
                            if type(result) is dict:
                                user.userId = result['userId']
                                user.requestId = result['requestId']
                            user.save()
                            return Response()
                    raise DigitsException()
                else:
                    print '    A pin was given'
                    device = request.data.get('device', False)
                    success = False
                    if device:
                        if not user.requestId and not user.userId:
                            # The user already got a message, but just got added to the Digits database
                            userId = self.confirmRegistration(digits, phone, pin)
                            user.userId = userId
                            user.save()
                            success = True
                        else:
                            # The user already was in the Digits database and got a request and user id
                            userId = self.confirmSignin(digits, user.requestId, user.userId, pin)
                            success = True

                        if success:
                            token = Token(device=device, user=user)
                            token.save()
                            tokenSerializer = TokenSerializer(token)
                            return Response(tokenSerializer.data)

        raise InvalidRequest()
