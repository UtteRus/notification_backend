#!/bin/bash
set -e

echo "Выполняем миграции."
python manage.py migrate --noinput

exec "$@"
