from rest_framework.versioning import BaseVersioning


class HeaderVersioning(BaseVersioning):
    default_version = 1
    allowed_versions = [1]

    def determine_version(self, request, *args, **kwargs):
        return int(request.META.get('HTTP_X_VERSION', HeaderVersioning.default_version))
