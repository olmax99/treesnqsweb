#!/usr/bin/env sh
set -e

#-------------------- Gunicorn Parameters-----------------------------

# Accepting wsgi.py in either '/opt/app' or '/opt/app/app'
if [ -f /opt/app/app/wsgi.py ]; then
    DEFAULT_MODULE_NAME=app.wsgi
elif [ -f /opt/app/wsgi.py ]; then
    DEFAULT_MODULE_NAME=wsgi
fi
# Specifiy 'MODULE_NAME' as environment variable or take wsgi.py
# Default is APP_MODULE="app.wsgi:application"
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-application}

export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

# Searching for gunicorn_conf in '/', '/app', '/app/app'
if [ -f /opt/app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/app/gunicorn_conf.py
elif [ -f /opt/app/app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/app/app/gunicorn_conf.py
else
    DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
fi

export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}

# Basically redirects the variables APP_MODULE and GUNICORN_CONF to CMD
exec "$@"
