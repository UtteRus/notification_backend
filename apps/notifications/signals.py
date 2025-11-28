from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.notifications.choices import NotificationStatusChoices
from apps.notifications.models import Notification
from apps.notifications.tasks import send_notification


@receiver(post_save, sender=Notification)
def create_periodic_task(sender, instance, created, **kwargs):
    """Создает периодическую задачу при создании уведомления."""
    if created and instance.status == NotificationStatusChoices.PENDING:
        send_notification.delay(instance)
