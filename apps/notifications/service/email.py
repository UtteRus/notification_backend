from django.conf import settings
from django.core.mail import send_mail

from apps.notifications.service.base_service import BaseServiceMixin


class EmailService(BaseServiceMixin):
    """Сервис для отправки уведомлений по email"""

    @staticmethod
    def send(
        user_email: str,
        subject: str,
        message: str,
    ) -> tuple[bool, str | None, dict | None]:
        """
        Отправляет email уведомление

        Args:
            user_email: Email адрес получателя
            subject: Тема письма
            message: Текст сообщения

        Returns:
            tuple: (успех, ошибка, данные_ответа)
        """
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')

        if not from_email:
            error = 'Email не настроен: отсутствует адрес отправителя'
            return False, error, None

        if not user_email:
            error = 'Email получателя не указан'
            return False, error, None

        if not message:
            error = 'Сообщение не указано'
            return False, error, None

        try:
            send_mail(
                subject=subject or 'Уведомление',
                message=message,
                from_email=from_email,
                recipient_list=[user_email],
                fail_silently=False,
            )

            return True, None, {'recipient': user_email, 'subject': subject}

        except Exception as e:
            error = f'Ошибка отправки email: {str(e)}'
            return False, error, None

    @staticmethod
    def can_send(user) -> bool:
        """Проверяет, можно ли отправить email пользователю"""
        if not user:
            return False

        email = getattr(user, 'email', None)
        return bool(email)
