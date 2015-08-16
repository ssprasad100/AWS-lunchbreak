from rest_framework.versioning import BaseVersioning


class HeaderVersioning(BaseVersioning):

    def determine_version(self, request, *args, **kwargs):
        return request.META.get('HTTP_X_VERSION', 1)
