from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from apps.notifications.choices import DeliveryStatusChoices, NotificationStatusChoices, NotificationTypeChoices

User = get_user_model()


class Notification(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Уведомление',
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Тема уведомления',
    )
    message = models.TextField(
        verbose_name='Текст уведомления',
    )
    channels = ArrayField(
        models.CharField(
            verbose_name='Вид доставки',
            choices=NotificationTypeChoices.choices,
        ),
        verbose_name='Вид доставки',
    )
    status = models.CharField(
        choices=NotificationStatusChoices.choices,
        default=NotificationStatusChoices.PENDING,
        verbose_name='Статус сообщения',
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время успешной отправки',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Время обновления',
    )

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.status} - {self.created_at}'

    def mark_as_sent(self):
        """Отмечает уведомление как отправленное"""

        self.status = NotificationStatusChoices.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])

    def mark_as_failed(self):
        """Отмечает уведомление как неудачное"""
        self.status = NotificationStatusChoices.FAILED
        self.save(update_fields=['status', 'updated_at'])


class NotificationLog(models.Model):
    notification = models.ForeignKey(
        to='Notification',
        on_delete=models.CASCADE,
        related_name='delivery_logs',
        verbose_name='Уведомление',
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationTypeChoices.choices,
        verbose_name='Канал доставки',
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatusChoices.choices,
        verbose_name='Статус доставки',
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Сообщение об ошибке',
    )
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время попытки',
    )
    response_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Данные ответа от провайдера',
    )

    class Meta:
        verbose_name = 'Лог доставки'
        verbose_name_plural = 'Логи доставки'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['notification', 'channel']),
            models.Index(fields=['status', 'attempted_at']),
        ]

    def __str__(self):
        return f'{self.notification.id} - {self.channel} - {self.status}'
