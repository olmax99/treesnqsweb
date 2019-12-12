from .base import *

from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = config('DJANGOAPP_FERNET_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# TODO: Move to k8s ConfigMap object
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': '5432',
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/opt/static/'
STATIC_ROOT = '/opt/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/opt/media/'
MEDIA_ROOT = '/opt/media/'

# Stripe Payments
# https://dashboard.stripe.com/test/dashboard

# Publishable Key pk_test_5fmmEWu1gFayFdYFmctskmcX006YNB5lQl
STRIPE_LIVE_PUBLIC_KEY = os.environ["DJANGOAPP_STRIPE_LIVE_PUBLIC_KEY"]
STRIPE_LIVE_SECRET_KEY = os.environ["DJANGOAPP_STRIPE_LIVE_SECRET_KEY"]
STRIPE_TEST_PUBLIC_KEY = os.environ["DJANGOAPP_STRIPE_TEST_PUBLIC_KEY"]
STRIPE_TEST_SECRET_KEY = os.environ["DJANGOAPP_STRIPE_TEST_SECRET_KEY"]
DJSTRIPE_WEBHOOK_SECRET = os.environ["DJANGOAPP_DJSTRIPE_WEBHOOK_SECRET"]
# TODO: Move to k8s ConfigMap object
# Change to True in production
STRIPE_LIVE_MODE = False