from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = 'apps.notifications'

    def ready(self):
        """
        Регистрация сигналов при загрузке приложения.
        """
        import apps.notifications.signals as signals  # noqa: F401
