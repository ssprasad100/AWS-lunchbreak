from django.apps import AppConfig


class CustomersConfig(AppConfig):
    name = 'customers'
    verbose_name = 'Consumenten'

    def ready(self):
        from . import receivers, signals  # NOQA
