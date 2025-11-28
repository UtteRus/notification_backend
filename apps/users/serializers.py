from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'telegram_chat_id',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login',
        ]
