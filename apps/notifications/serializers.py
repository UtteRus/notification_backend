from rest_framework import serializers

from apps.notifications.models import Notification, NotificationLog


class NotificationLogSerializer(serializers.ModelSerializer):
    """Сериализатор для логов доставки"""

    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'notification',
            'channel',
            'status',
            'error_message',
            'attempted_at',
            'response_data',
        ]
        read_only_fields = ['id', 'attempted_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений"""

    delivery_logs = NotificationLogSerializer(many=True, read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'subject',
            'message',
            'channels',
            'status',
            'sent_at',
            'created_at',
            'updated_at',
            'delivery_logs',
        ]
        read_only_fields = [
            'id',
            'status',
            'sent_at',
            'created_at',
            'updated_at',
            'delivery_logs',
        ]
