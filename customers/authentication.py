from customers.exceptions import AuthenticationFailed
from customers.models import User
from rest_framework import authentication


class LunchbreakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_IDENTIFIER')
        userId = request.META.get('HTTP_USER')
        device = request.META.get('HTTP_DEVICE')

        if not identifier or not userId or not device:
            raise AuthenticationFailed('Not all of the headers were provided.')

        try:
            user = User.objects.get(id=userId)
            user.usertoken_set.get(identifier=identifier, device=device)
        except:
            raise AuthenticationFailed('User not found.')

        return (user, None)
