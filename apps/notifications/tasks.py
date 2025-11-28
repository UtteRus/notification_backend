from celery import shared_task

from apps.notifications.choices import DeliveryStatusChoices, NotificationStatusChoices
from apps.notifications.models import Notification, NotificationLog
from apps.notifications.service.email import EmailService
from apps.notifications.service.sms import SMSService
from apps.notifications.service.telegram import TelegramService


@shared_task
def send_notification(notification):
    """Отправляет уведомление."""

    user = notification.user
    for channel in notification.channels or []:
        success, error, response = _send_via_channel(notification, channel, user)
        if success:
            NotificationLog.objects.create(
                notification=notification,
                channel=channel,
                status=DeliveryStatusChoices.SUCCESS,
                error_message=error,
                response_data=response,
            )
            notification.mark_as_sent()
            return
        NotificationLog.objects.create(
            notification=notification,
            channel=channel,
            status=DeliveryStatusChoices.FAILED,
            error_message=error,
            response_data=response,
        )
    notification.mark_as_failed()


def _send_via_channel(notification, channel, user):
    """Отправляет через указанный канал."""
    if channel == 'email':
        return EmailService.send(
            user_email=user.email,
            subject=notification.subject or 'Уведомление',
            message=notification.message,
        )

    if channel == 'sms':
        phone = getattr(user, 'phone_number', None)
        return SMSService.send(phone_number=phone, message=notification.message)

    if channel == 'telegram':
        chat_id = getattr(user, 'telegram_chat_id', None)
        return TelegramService.send(chat_id=str(chat_id), message=notification.message)

    return False, f'Неизвестный канал: {channel}', None
