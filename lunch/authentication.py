from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        identifier = request.META.get('HTTP_X_IDENTIFIER')
        modelId = request.META.get('HTTP_X_' + self.MODEL_NAME.upper())
        device = request.META.get('HTTP_X_DEVICE')

        if not identifier or not modelId or not device:
            raise AuthenticationFailed('Not all of the headers were provided.')

        try:
            arguments = {
                self.MODEL_NAME + '_id': modelId,
                'device': device
            }
            modelTokens = self.TOKEN_MODEL.objects.select_related(
                self.MODEL_NAME
            ).filter(
                **arguments
            )
            for modelToken in modelTokens:
                if modelToken.checkIdentifier(identifier):
                    return (getattr(modelToken, self.MODEL_NAME), modelToken)
        except self.TOKEN_MODEL.DoesNotExist:
            pass
        raise AuthenticationFailed(
            '{modelName}Token not found.'.format(
                modelName=self.MODEL_NAME.capitalize()
            )
        )


class PrivateMediaAuthentication(object):

    def has_read_permission(self, request, path):
        from customers.authentication import CustomerAuthentication
        try:
            CustomerAuthentication().authenticate(request)
            return True
        except AuthenticationFailed:
            return False
