from rest_framework import authentication, exceptions

from lunch.models import User


class LunchbreakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_IDENTIFIER')
        digitsId = request.META.get('HTTP_DIGITS')
        device = request.META.get('HTTP_DEVICE')

        print request.META

        if not identifier or not digitsId or not device:
            raise exceptions.AuthenticationFailed('User authentication failed: No headers provided')

        try:
            user = User.objects.get(digitsId=digitsId)
            user.token_set.get(identifier=identifier, device=device)
        except:
            raise exceptions.AuthenticationFailed('User authentication failed: invalid headers')

        return (user, None)
