#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Production settings and globals."""

from os import environ

from base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


# HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/
# #allowed-hosts-required-in-production
ALLOWED_HOSTS = []
# END HOST CONFIGURATION

# EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = environ.get('ACTIVITY_EMAIL_HOST', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('ACTIVITY_EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('ACTIVITY_EMAIL_HOST_USER', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('ACTIVITY_EMAIL_PORT', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
# END EMAIL CONFIGURATION

# DATABASE CONFIGURATION
# DATABASE CONFIGURATION
DATABASES = {
    'default': {
        # 'django.db.backends.postgresql'
        'ENGINE': environ.get('ACTIVITY_PROD_DB_ENGINE', ''),
        'NAME': environ.get('ACTIVITY_PROD_DB_NAME', ''),
        'USER': environ.get('ACTIVITY_PROD_DB_USER', ''),
        'PASSWORD': environ.get('ACTIVITY_PROD_DB_PASSWORD', ''),
        'HOST': environ.get('ACTIVITY_PROD_DB_HOST', ''),
        'PORT': environ.get('ACTIVITY_PROD_DB_PORT', ''),
    }
}

GOOGLE_MAP_API_KEY = environ.get('ACTIVITY_GOOGLE_MAP_API_KEY', '')

# END DATABASE CONFIGURATION


# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {}
# END CACHE CONFIGURATION


# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('ACTIVITY_SECRET_KEY')
# END SECRET CONFIGURATION

REPORT_SERVER = False
OFFLINE_MODE = False
NON_LDAP = True