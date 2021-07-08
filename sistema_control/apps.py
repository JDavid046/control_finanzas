from django.apps import AppConfig


class SistemaControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sistema_control'

    def ready(self):
        from . import signals
