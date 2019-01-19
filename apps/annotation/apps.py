from django.apps import AppConfig

class AnnotationConfig(AppConfig):
    name = 'apps.annotation'

    def ready(self):
        # Register signals
        import apps.annotation.signals
