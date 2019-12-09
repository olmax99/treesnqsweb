#! /usr/bin/env sh

echo "Running inside /opt/app/prestart.sh, add migrations here:"
sleep 10

cd /opt
# python manage.py flush --no-input

# TODO: Set settings location dynamically
# Apply database migrations
echo "..apply database migrations"
python manage.py makemigrations --settings=app.settings.development
python manage.py migrate --settings=app.settings.development

# Apply Stripe payment migration
# python manage.py djstripe_init_customers

# Collect static files
echo "..collecting static files"
python manage.py collectstatic --noinput --settings=app.settings.development
