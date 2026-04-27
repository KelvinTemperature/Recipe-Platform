#!/bin/sh
python manage.py migrate --noinput
echo "from accounts.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@gmail.com', 'Admin1234!', role='admin')" | python manage.py shell
gunicorn recipe_platform.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120