from django.contrib.auth import get_user_model

from apps.notifications.choices import (
    DeliveryStatusChoices,
    NotificationStatusChoices,
    NotificationTypeChoices,
)
from apps.notifications.models import Notification, NotificationLog
from apps.notifications.service.email import EmailService
from apps.notifications.service.sms import SMSService
from apps.notifications.service.telegram import TelegramService
from apps.notifications.tasks import process_notification

User = get_user_model()


class NotificationService:
    """Основной сервис для управления уведомлениями с fallback механизмом"""

    # Маппинг каналов на сервисы
    CHANNEL_SERVICES = {
        NotificationTypeChoices.EMAIL: EmailService,
        NotificationTypeChoices.SMS: SMSService,
        NotificationTypeChoices.TELEGRAM: TelegramService,
    }

    @classmethod
    def create_notification(
        cls,
        user: User,
        message: str,
        subject: str = '',
        channels: list[str] | None = None,
    ) -> Notification:
        """
        Создает уведомление и запускает задачу на отправку

        Args:
            user: Пользователь-получатель
            message: Текст уведомления
            subject: Тема (для email)
            channels: Список каналов доставки (по умолчанию все доступные)

        Returns:
            Notification: Созданное уведомление
        """
        if channels is None:
            channels = cls.get_available_channels(user)

        notification = Notification.objects.create(
            user=user,
            message=message,
            subject=subject,
            channels=channels,
            status=NotificationStatusChoices.PENDING,
        )

        process_notification.delay(notification.id)

        return notification

    @classmethod
    def get_available_channels(cls, user: User) -> list[str]:
        """
        Возвращает список доступных каналов для пользователя

        Args:
            user: Пользователь

        Returns:
            List[str]: Список доступных каналов
        """
        available = []

        for channel, service_class in cls.CHANNEL_SERVICES.items():
            if service_class.can_send(user):
                available.append(channel)

        if not available:
            available = [NotificationTypeChoices.EMAIL]

        return available

    @classmethod
    def send_via_channel(
        cls,
        notification: Notification,
        channel: str,
    ) -> tuple[bool, str | None, dict | None]:
        """
        Отправляет уведомление через указанный канал

        Args:
            notification: Объект уведомления
            channel: Канал доставки

        Returns:
            tuple: (success: bool, error_message: Optional[str], response_data: Optional[dict])
        """
        service_class = cls.CHANNEL_SERVICES.get(channel)
        if not service_class:
            error_msg = f'Неизвестный канал доставки: {channel}'
            return False, error_msg, None

        # Получаем данные пользователя для канала
        user = notification.user

        try:
            if channel == NotificationTypeChoices.EMAIL:
                success, error, response = service_class.send(
                    user_email=user.email,
                    subject=notification.subject or 'Уведомление',
                    message=notification.message,
                )
            elif channel == NotificationTypeChoices.SMS:
                phone = getattr(user, 'phone_number', None) or getattr(user, 'phone', None)
                success, error, response = service_class.send(
                    phone_number=phone,
                    message=notification.message,
                )
            elif channel == NotificationTypeChoices.TELEGRAM:
                chat_id = getattr(user, 'telegram_chat_id', None) or getattr(user, 'telegram_id', None)
                success, error, response = service_class.send(
                    chat_id=str(chat_id),
                    message=notification.message,
                )
            else:
                return False, f'Неподдерживаемый канал: {channel}', None

            return success, error, response

        except AttributeError as e:
            error_msg = f'У пользователя отсутствует необходимый атрибут для канала {channel}: {str(e)}'
            return False, error_msg, None
        except Exception as e:
            error_msg = f'Неожиданная ошибка при отправке через {channel}: {str(e)}'
            return False, error_msg, None

    @classmethod
    def log_delivery_attempt(
        cls,
        notification: Notification,
        channel: str,
        success: bool,
        error_message: str | None = None,
        response_data: dict | None = None,
    ) -> NotificationLog:
        """
        Логирует попытку доставки

        Args:
            notification: Объект уведомления
            channel: Канал доставки
            success: Успешность доставки
            error_message: Сообщение об ошибке
            response_data: Данные ответа от провайдера

        Returns:
            NotificationLog: Созданная запись лога
        """
        status = DeliveryStatusChoices.SUCCESS if success else DeliveryStatusChoices.FAILED

        return NotificationLog.objects.create(
            notification=notification,
            channel=channel,
            status=status,
            error_message=error_message,
            response_data=response_data,
        )
