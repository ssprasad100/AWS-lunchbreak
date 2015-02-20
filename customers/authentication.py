from customers.exceptions import AuthenticationFailed
from customers.models import UserToken
from rest_framework import authentication


class CustomerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_IDENTIFIER')
        userId = request.META.get('HTTP_USER')
        device = request.META.get('HTTP_DEVICE')

        if not identifier or not userId or not device:
            raise AuthenticationFailed('Not all of the headers were provided.')

        try:
            userToken = UserToken.objects.get(user_id=userId, identifier=identifier, device=device)
        except:
            raise AuthenticationFailed('UserToken not found.')

        return (userToken.user, None)
