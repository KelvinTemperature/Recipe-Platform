#!/bin/sh
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
gunicorn recipe_platform.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120