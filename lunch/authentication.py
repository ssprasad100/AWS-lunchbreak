from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_X_IDENTIFIER')
        modelId = request.META.get('HTTP_X_' + self.MODEL_NAME.upper())
        device = request.META.get('HTTP_X_NAME') if request.version > 2 else request.META.get('HTTP_X_DEVICE')

        if not identifier or not modelId or not device:
            raise AuthenticationFailed('Not all of the headers were provided.')

        try:
            arguments = {self.MODEL_NAME + '_id': modelId, 'identifier': identifier, 'name': device}
            modelToken = self.TOKEN_MODEL.objects.get(**arguments)
        except:
            raise AuthenticationFailed('%sToken not found.' % self.MODEL_NAME.capitalize())

        return (getattr(modelToken, self.MODEL_NAME), None)
