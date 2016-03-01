from lunch.authentication import TokenAuthentication

from .exceptions import UserDisabled
from .models import UserToken


class CustomerAuthentication(TokenAuthentication):
    TOKEN_MODEL = UserToken
    MODEL_NAME = 'user'

    def authenticate(self, request):
        user, userToken = super(CustomerAuthentication, self).authenticate(request)
        if not user.enabled:
            raise UserDisabled()
        return (user, userToken,)
