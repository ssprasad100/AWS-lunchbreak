from rest_framework import status, viewsets
from rest_framework.response import Response


class TargettedViewSet(viewsets.GenericViewSet):

    def get_attr_action(self, attribute):
        action_attribute = '{attribute}_{action}'.format(
            attribute=attribute,
            action=self.action
        )
        try:
            return getattr(self, action_attribute)
        except AttributeError:
            return getattr(super(), 'get_' + attribute)()

    def get_object(self):
        return self.get_attr_action('object')

    def get_serializer_class(self):
        return self.get_attr_action('serializer_class')

    def get_queryset(self):
        return self.get_attr_action('queryset')

    def get_pagination_class(self):
        return self.get_attr_action('pagination_class')

    def get_serializer_context(self):
        return self.get_attr_action('serializer_context')

    def _list(self, request):
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
