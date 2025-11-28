from django.db.models import TextChoices


class NotificationStatusChoices(TextChoices):
    SENT = 'sent', 'Отправлено'
    PENDING = 'pending', 'В ожидании'
    FAILED = 'failed', 'Ошибка доставки'


class NotificationTypeChoices(TextChoices):
    EMAIL = 'email', 'Электронная почта'
    SMS = 'sms', 'СМС'
    TELEGRAM = 'telegram', 'Телеграм'


class DeliveryStatusChoices(TextChoices):
    SUCCESS = 'success', 'Успешно'
    FAILED = 'failed', 'Ошибка'
    PENDING = 'pending', 'В обработке'
