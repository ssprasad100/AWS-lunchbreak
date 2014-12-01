from rest_framework import authentication, exceptions

from lunch.models import User


class LunchbreakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_IDENTIFIER')
        userId = request.META.get('HTTP_USER')
        device = request.META.get('HTTP_DEVICE')

        if not identifier or not userId or not device:
            raise exceptions.AuthenticationFailed('User authentication failed: No headers provided')

        try:
            user = User.objects.get(userId=userId)
            user.token_set.get(identifier=identifier, device=device)
        except:
            raise exceptions.AuthenticationFailed('User authentication failed: invalid headers')

        return (user, None)
