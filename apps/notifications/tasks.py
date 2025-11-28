from celery import shared_task

from apps.notifications.choices import NotificationStatusChoices
from apps.notifications.models import Notification
from apps.notifications.service import NotificationService


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_notification(self, notification_id: int):
    """
    Задача для отправки уведомления, если способ не доступен, используем другой.

    Args:
        notification_id: ID уведомления
    """
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return

    if notification.status == NotificationStatusChoices.SENT:
        return

    channels = notification.channels or []

    if not channels:
        notification.mark_as_failed()
        return

    for channel in channels:
        success, error_message, response_data = NotificationService.send_via_channel(
            notification=notification,
            channel=channel,
        )

        NotificationService.log_delivery_attempt(
            notification=notification,
            channel=channel,
            success=success,
            error_message=error_message,
            response_data=response_data,
        )

        if success:
            notification.mark_as_sent()
            return
        continue

    notification.mark_as_failed()


@shared_task(bind=True, max_retries=5, default_retry_delay=300)
def retry_failed_notification(self, notification_id: int):
    """
    Задача для повторной попытки отправки неудачных уведомлений

    Args:
        notification_id: ID уведомления
    """
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return

    notification.status = NotificationStatusChoices.PENDING
    notification.save(update_fields=['status', 'updated_at'])

    process_notification.delay(notification_id)
