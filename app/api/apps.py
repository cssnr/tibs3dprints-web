from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"
    verbose_name = "API"

    # def ready(self):
    #     import api.signals  # noqa: F401
