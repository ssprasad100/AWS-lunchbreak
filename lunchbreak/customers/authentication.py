from lunch.authentication import TokenAuthentication
from Lunchbreak.exceptions import LunchbreakException

from .exceptions import UserDisabled
from .models import User, UserToken


class CustomerAuthentication(TokenAuthentication):
    TOKEN_MODEL = UserToken
    MODEL_NAME = 'user'

    def authenticate(self, request):
        user, userToken = super(CustomerAuthentication, self).authenticate(request)
        if not user.enabled:
            raise UserDisabled()
        return (user, userToken,)


class CustomerBackend(CustomerAuthentication):

    def authenticate(self, identifier=None, device=None, phone=None):
        if not identifier or not device or not phone:
            return None

        try:
            user, usertoken = self._authenticate(
                identifier=identifier,
                device=device,
                filter_args={
                    'user__phone': phone
                }
            )
        except LunchbreakException:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(
                id=user_id
            )
        except User.DoesNotExist:
            return None
