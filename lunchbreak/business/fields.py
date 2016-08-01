from rest_framework.fields import CurrentUserDefault


class CurrentUserAttributeDefault(CurrentUserDefault):

    def __init__(self, attribute):
        self.attributes = attribute.split('.')

    def __call__(self):
        # value defaults to user
        value = super().__call__()
        for attribute in self.attributes:
            value = getattr(value, attribute, None)
        return value
