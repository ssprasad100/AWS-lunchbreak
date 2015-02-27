from customers.models import UserToken
from lunch.authentication import TokenAuthentication


class CustomerAuthentication(TokenAuthentication):
    FOREIGN_KEY_ATTRIBUTE = 'user'
    FOREIGN_KEY_TOKEN = UserToken
