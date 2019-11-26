#! /usr/bin/env sh

echo "Running inside /opt/app/prestart.sh, add migrations here:"
sleep 10

cd /opt
# python manage.py flush --no-input

# Apply database migrations
echo "..apply database migrations"
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "..collecting static files"
python manage.py collectstatic --noinput
