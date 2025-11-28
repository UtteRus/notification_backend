from django.contrib.auth import get_user_model
from rest_framework import viewsets

from apps.users.serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
