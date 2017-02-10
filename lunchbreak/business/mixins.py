from django.apps import apps
from rest_framework import status
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response


class NotifyModelMixin:

    @classmethod
    def _notify(cls, message, instance=None, queryset=None, **kwargs):
        if queryset is None:
            if instance is None:
                raise ValueError('Either instance or queryset must be not None.')
            queryset = instance.tokens.all()
        else:
            model_name = queryset.model.__name__
            token_model = apps.get_model(
                'business.{model}Token'.format(
                    model=model_name
                )
            )
            queryset = token_model.objects.filter(
                **{
                    model_name.lower() + '__in': queryset
                }
            )

        kwargs.setdefault('sound', 'default')
        queryset.send_message(
            message,
            **kwargs
        )

    def notify(self, message, **kwargs):
        self._notify(
            message=message,
            instance=self,
            **kwargs
        )


class SafeDeleteModelMixin(DestroyModelMixin):
    """Delete a model instance.model

    Return 200 if the model was safe deleted,
    return 204 if the model was hard deleted.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance.pk is not None:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
