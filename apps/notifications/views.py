from rest_framework import viewsets

from apps.notifications.models import Notification, NotificationLog
from apps.notifications.serializers import NotificationSerializer, NotificationLogSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с уведомлениями"""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра логов доставки (только чтение)"""

    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer