#!/bin/bash
echo "Starting application..."
. /app/.venv/bin/activate
echo "Virtual environment activated."

python manage.py migrate --no-input
echo "Migrations applied."
python manage.py collectstatic --noinput

if [ "${DEBUG:-0}" = "1" ]; then
    exec python manage.py runserver 0.0.0.0:8000
else
    exec uvicorn configs.asgi:application --host 0.0.0.0 --port 8000
fi

