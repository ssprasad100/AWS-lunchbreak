from lunch.exceptions import AuthenticationFailed
from rest_framework import authentication


class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_X_IDENTIFIER')
        modelId = request.META.get('HTTP_X_' + self.FOREIGN_KEY_ATTRIBUTE.upper())
        device = request.META.get('HTTP_X_DEVICE')

        if not identifier or not modelId or not device:
            raise AuthenticationFailed('Not all of the headers were provided.')

        try:
            arguments = {self.FOREIGN_KEY_ATTRIBUTE + '_id': modelId, 'identifier': identifier, 'device': device}
            modelToken = self.FOREIGN_KEY_TOKEN.objects.get(**arguments)
        except:
            raise AuthenticationFailed('%sToken not found.' % self.FOREIGN_KEY_ATTRIBUTE.capitalize())

        return (getattr(modelToken, self.FOREIGN_KEY_ATTRIBUTE), None)
