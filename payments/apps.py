from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'

    def ready(self):
        # return super().ready()
        # Import scheduler here to avoid running it multiple times in dev server reloads
        from . import scheduler
        scheduler.start()