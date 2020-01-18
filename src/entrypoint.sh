#!/bin/sh

echo "Waiting for pepega database.."
# set -e
until mysql --host=$SQL_HOST --port=$SQL_PORT --user=$SQL_USER --password=$SQL_PASSWORD --execute='\q' $SQL_DATABASE; do
    >&2 echo "still waiting for db ResidentSleeper.."
    sleep 1
done 
>&2 echo "db is up PogChamp"

echo "monkaS"

python manage.py migrate &&

exec "$@"
