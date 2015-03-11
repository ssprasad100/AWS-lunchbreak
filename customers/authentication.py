from customers.models import UserToken
from lunch.authentication import TokenAuthentication


class CustomerAuthentication(TokenAuthentication):
    TOKEN_MODEL = UserToken
    MODEL_NAME = 'user'
