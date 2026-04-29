from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import os
        # Only start scheduler in the main process (not in Django's reloader child)
        if os.environ.get('RUN_MAIN') != 'true':
            from core.scheduler import start
            start()
