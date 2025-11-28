import requests
from django.conf import settings

from apps.notifications.service.base_service import BaseServiceMixin


class TelegramService(BaseServiceMixin):
    """Сервис для отправки сообщений через Telegram Bot API"""

    # URL Telegram Bot API
    API_URL = 'https://api.telegram.org/bot{token}/sendMessage'

    @staticmethod
    def send(chat_id: str, message: str) -> tuple[bool, str | None, dict | None]:
        """
        Отправляет сообщение в Telegram

        Args:
            chat_id: ID чата в Telegram (число или строка)
            message: Текст сообщения

        Returns:
            tuple: (успех, ошибка, данные_ответа)
        """
        # Получаем токен бота
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

        # Проверяем настройки
        if not token:
            error = 'Telegram не настроен: отсутствует токен бота'
            return False, error, None

        # Проверяем параметры
        if not chat_id:
            error = 'ID чата не указан'
            return False, error, None

        if not message:
            error = 'Сообщение не указано'
            return False, error, None

        try:
            # Формируем URL с токеном
            url = TelegramService.API_URL.format(token=token)

            # Отправляем сообщение
            response = requests.post(
                url,
                json={
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                },
                timeout=10,
            )

            if response.status_code != 200:
                error = f'Ошибка API: {response.status_code}'
                return False, error, {'status_code': response.status_code}

            # Проверяем ответ
            data = response.json()

            if data.get('ok'):
                return (
                    True,
                    None,
                    {
                        'message_id': data.get('result', {}).get('message_id'),
                        'chat_id': chat_id,
                    },
                )
            error = data.get('description', 'Неизвестная ошибка Telegram API')
            return False, error, data

        except requests.exceptions.RequestException as e:
            error = f'Ошибка сети: {str(e)}'
            return False, error, None
        except Exception as e:
            error = f'Ошибка отправки Telegram: {str(e)}'
            return False, error, None

    @staticmethod
    def can_send(user) -> bool:
        """Проверяет, можно ли отправить сообщение пользователю"""
        if not user:
            return False

        chat_id = getattr(user, 'telegram_chat_id', None)
        return bool(chat_id)
