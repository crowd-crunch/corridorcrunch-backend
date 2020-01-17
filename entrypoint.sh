#!/bin/sh

echo "Waiting for the database to start..."
sleep 5
echo "Database started."

python manage.py flush --no-input
python manage.py migrate

exec "$@"
