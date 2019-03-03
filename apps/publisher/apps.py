from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.publisher'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import tasks
