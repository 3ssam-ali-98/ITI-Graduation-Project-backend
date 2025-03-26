from django.apps import AppConfig


class BusinessManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'business_management'

    def ready(self):
      # Implicitly connect signal handlers decorated with @receiver.
      from . import signals