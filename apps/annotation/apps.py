from django.apps import AppConfig


class Config(AppConfig):
    name = 'apps.annotation'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import tasks
        # noinspection PyUnresolvedReferences
        from . import signals
