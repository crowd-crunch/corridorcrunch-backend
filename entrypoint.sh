#!/bin/sh

echo "Waiting for 5 seconds.."
sleep 5

python manage.py flush --no-input
python manage.py migrate

exec "$@"
