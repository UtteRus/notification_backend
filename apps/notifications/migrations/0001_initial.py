import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, default='', max_length=255, verbose_name='Тема уведомления')),
                ('message', models.TextField(verbose_name='Текст уведомления')),
                ('channels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('email', 'Электронная почта'), ('sms', 'СМС'), ('telegram', 'Телеграм')], verbose_name='Вид доставки'), size=None, verbose_name='Вид доставки')),
                ('status', models.CharField(choices=[('sent', 'Отправлено'), ('pending', 'В ожидании'), ('failed', 'Ошибка доставки')], default='pending', verbose_name='Статус сообщения')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='Время успешной отправки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Уведомление')),
            ],
            options={
                'verbose_name': 'Уведомление',
                'verbose_name_plural': 'Уведомления',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(choices=[('email', 'Электронная почта'), ('sms', 'СМС'), ('telegram', 'Телеграм')], max_length=20, verbose_name='Канал доставки')),
                ('status', models.CharField(choices=[('success', 'Успешно'), ('failed', 'Ошибка'), ('pending', 'В обработке')], max_length=20, verbose_name='Статус доставки')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Сообщение об ошибке')),
                ('attempted_at', models.DateTimeField(auto_now_add=True, verbose_name='Время попытки')),
                ('response_data', models.JSONField(blank=True, null=True, verbose_name='Данные ответа от провайдера')),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_logs', to='notifications.notification', verbose_name='Уведомление')),
            ],
            options={
                'verbose_name': 'Лог доставки',
                'verbose_name_plural': 'Логи доставки',
                'ordering': ['-attempted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'status'], name='notificatio_user_id_7088ed_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['status', 'created_at'], name='notificatio_status_9a4505_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['notification', 'channel'], name='notificatio_notific_9169c3_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['status', 'attempted_at'], name='notificatio_status_76a2ce_idx'),
        ),
    ]
