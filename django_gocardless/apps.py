from django.apps import AppConfig


class DjangoGoCardlessAppConfig(AppConfig):
    name = 'django_gocardless'
    verbose_name = 'Django GoCardless'

    def ready(self):
        from django_gocardless import receivers, signals  # NOQA
