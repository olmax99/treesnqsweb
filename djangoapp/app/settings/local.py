from .base import *

import sys

from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGOAPP_FERNET_KEY')

# TODO: Move to k8s ConfigMap object
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (sys.argv[1] == 'runserver')
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['192.168.39.196', 'localhost', '127.0.0.1']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(process)d] [%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ['DJANGO_LOG_LEVEL'],
            'propagate': True,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
}


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'djangoapp_debug.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/media/'

