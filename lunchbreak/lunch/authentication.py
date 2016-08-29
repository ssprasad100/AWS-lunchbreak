from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class TokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        identifier = request.META.get('HTTP_X_IDENTIFIER')
        model_id = request.META.get('HTTP_X_' + self.MODEL_NAME.upper())
        device = request.META.get('HTTP_X_DEVICE')

        if not identifier or not model_id or not device:
            raise AuthenticationFailed('Not all of the headers were provided.')

        return self._authenticate(
            identifier=identifier,
            device=device,
            filter_args={
                self.MODEL_NAME + '_id': model_id
            },
        )

    def _authenticate(self, identifier=None, device=None, filter_args={}):
        if identifier is None or device is None or not filter_args:
            raise AuthenticationFailed(
                'Either model_id or phone must be passed to TokenAuthentication._authenticate.'
            )

        try:
            arguments = {
                'device': device
            }
            arguments.update(filter_args)

            model_tokens = self.TOKEN_MODEL.objects.select_related(
                self.MODEL_NAME
            ).filter(
                **arguments
            )
            for model_token in model_tokens:
                if model_token.check_identifier(identifier):
                    return (getattr(model_token, self.MODEL_NAME), model_token)
        except self.TOKEN_MODEL.DoesNotExist:
            pass
        raise AuthenticationFailed(
            '{model_name}Token not found.'.format(
                model_name=self.MODEL_NAME.capitalize()
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
