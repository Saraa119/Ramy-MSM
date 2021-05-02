from django.apps import AppConfig


class MedConfig(AppConfig):
    name = 'med'

    def ready(self):
        import med.signals