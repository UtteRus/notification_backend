from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import NotificationLogViewSet, NotificationViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('notification-logs', NotificationLogViewSet, basename='notification-log')

urlpatterns = [
    path('', include(router.urls)),
]
