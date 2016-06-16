from rest_framework import status, viewsets
from rest_framework.response import Response


class TargettedViewSet(viewsets.GenericViewSet):

    def get_attr_action(self, attribute):
        action_attribute = '{attribute}_{action}'.format(
            attribute=attribute,
            action=self.action
        )
        return getattr(self, action_attribute, None)

    def get_object(self):
        return self.get_attr_action('object') or \
            super().get_object()

    def get_serializer_class(self):
        return self.get_attr_action('serializer_class') or \
            super().get_serializer_class()

    def get_queryset(self):
        return self.get_attr_action('queryset') or \
            super().get_queryset()

    def get_pagination_class(self):
        return self.get_attr_action('pagination_class') or \
            super().get_pagination_class()

    def get_serializer_context(self):
        return self.get_attr_action('serializer_context') or \
            super().get_serializer_context()

    def _list(self, request):
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
