from django.apps import AppConfig

class DiagnosticAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diagnostic_app'
    verbose_name = 'Diagnostic App'

    # def ready(self):
    #     import diagnostic_app.signals  # If you have signals