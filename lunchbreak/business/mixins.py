from django.apps import apps


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
