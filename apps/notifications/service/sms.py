import time
from typing import Optional

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth


class SMSService:
    """Сервис для отправки SMS через MTS Omnichannel API"""

    # URL API MTS
    API_SEND_URL = settings.API_SEND_URL
    API_CHECK_URL = settings.API_CHECK_URL

    @staticmethod
    def send(phone_number: str, message: str) -> tuple[bool, str | None, dict | None]:
        """
        Отправляет SMS сообщение

        Args:
            phone_number: Номер телефона в формате 79991234567
            message: Текст сообщения

        Returns:
            tuple: (успех, ошибка, данные_ответа)
        """
        login = getattr(settings, 'SMS_LOGIN', '')
        password = getattr(settings, 'SMS_PASSWORD', '')
        naming = getattr(settings, 'SMS_NAMING', '')

        if not all([login, password, naming]):
            error = 'SMS не настроен: отсутствуют учетные данные'
            return False, error, None

        if not phone_number:
            error = 'Номер телефона не указан'
            return False, error, None

        try:
            response = SMSService._send(login, password, naming, phone_number, message)

            if response.status_code != 200:
                error = f'Ошибка API: {response.status_code}'
                return False, error, {'status_code': response.status_code}

            data = response.json()
            message_id = data.get('messages', [{}])[0].get('internal_id')

            if not message_id:
                error = 'Не получен ID сообщения'
                return False, error, data

            time.sleep(3)
            status_ok = SMSService._check_status(login, password, message_id)

            if status_ok:
                return True, None, {'message_id': message_id, 'phone': phone_number}
            error = 'Сообщение отправлено, но статус не подтвержден'
            return False, error, {'message_id': message_id}

        except requests.exceptions.RequestException as e:
            error = f'Ошибка сети: {str(e)}'
            return False, error, None
        except Exception as e:
            error = f'Ошибка отправки SMS: {str(e)}'
            return False, error, None

    @staticmethod
    def _send(login: str, password: str, naming: str, phone: str, text: str) -> requests.Response:
        """Отправляет сообщение через API"""
        body = {
            'messages': [{'content': {'short_text': text}, 'from': {'sms_address': naming}, 'to': [{'msisdn': phone}]}]
        }

        return requests.post(
            SMSService.API_SEND_URL,
            json=body,
            auth=HTTPBasicAuth(login, password),
            timeout=10,
        )

    @staticmethod
    def _check_status(login: str, password: str, message_id: str) -> bool:
        """Проверяет статус доставки сообщения"""
        try:
            body = {'int_ids': [message_id]}
            response = requests.post(
                SMSService.API_CHECK_URL,
                json=body,
                auth=HTTPBasicAuth(login, password),
                timeout=10,
            )

            if response.status_code != 200:
                return False

            data = response.json()
            status = data.get('events_info', [{}])[0].get('events_info', [{}])[0].get('status')

            return status == 200

        except Exception:
            return False

    @staticmethod
    def can_send(user) -> bool:
        """Проверяет, можно ли отправить SMS пользователю"""
        if not user:
            return False

        phone = getattr(user, 'phone_number', None) or getattr(user, 'phone', None)
        return bool(phone)
