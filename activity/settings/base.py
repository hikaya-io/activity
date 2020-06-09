#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Common settings and globals."""

import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path

# PATH CONFIGURATION
# BASE DIR
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type
# our project name in our dotted import paths:
path.append(DJANGO_ROOT)
# END PATH CONFIGURATION


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
# END DEBUG CONFIGURATION


# MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

INTERNAL_IPS = [
    '127.0.0.1',
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# END MANAGER CONFIGURATION


# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }
# END DATABASE CONFIGURATION


# GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/Los_Angeles'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'fr-FR'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

LOCALE_PATHS = (
    normpath(join(SITE_ROOT, 'templates/locale')),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

DATE_FORMAT = 'Y-n-d'
# END GENERAL CONFIGURATION


# MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'


# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
# #std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
# #staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
# END STATIC FILE CONFIGURATION


# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = os.environ.get('SECRET_KEY', '!0^+)=t*ly6ycprf9@kfw$6fsjd0xoh#pa*2erx1m*lp5k9ko7')
# END SECRET CONFIGURATION


# SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0']
# END SITE CONFIGURATION


# FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/
# #std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
# END FIXTURE CONFIGURATION


# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/
# #template-context-processors

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'APP_DIRS': True,
        'DIRS': [
            normpath(join(SITE_ROOT, 'templates')),
            normpath(join(SITE_ROOT, 'customdashboard', 'templates')),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.tz',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'activity.processor.google_analytics',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ],
            'debug': DEBUG
        },
    },
]

# END TEMPLATE CONFIGURATION


# MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'activity.middleware.TimingMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
)
# END MIDDLEWARE CONFIGURATION


# REST CONFIGURATION
# Add Pagination to Rest Framework lists
REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'DEFAULT_FILTER_BACKENDS':
        ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# END REST CONFIGURATION


# URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
# END URL CONFIGURATION


# APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'social_django',
    # 'social.apps.django_app.default'
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_tables2',
    'crispy_forms',
    'django_extensions',
    'mathfilters',
    'import_export',
    'django_wysiwyg',
    'ckeditor',
    'ckeditor_uploader',
    'simplejson',
    'simple_history',
    'django_select2',
    'debug_toolbar'
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'workflow',
    'formlibrary',
    'activity',
    'feed',
    'indicators',
    'customdashboard',
    # 'configurabledashboard',
    'tables',
    'reports',
    'adminreport',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# END APP CONFIGURATION

# ###### AUTHENTICATION BAKEND CONFIG ######
# https://github.com/django/django/blob/master/django/contrib/auth/backends.py
AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.open_id.OpenIdAuth',
    # 'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    # 'social_core.backends.google.GoogleOAuth',
    # 'social_core.backends.twitter.TwitterOAuth',
    # 'social_core.backends.yahoo.YahooOpenId',
    # 'django.contrib.auth.backends.ModelBackend',
    'activity.middlewares.custom_middlewares.EmailOrUsernameBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# ########### END OF AUTHENTICATION BACKEND ##############

# ######### Login redirect ###########
LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGOUT_REDIRECT_URL = '/'

# LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

PROJECT_PATH = dirname(dirname(dirname(abspath(__file__))))
path.append(PROJECT_PATH)


# LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'filters': {
#        'require_debug_false': {
#            '()': 'django.utils.log.RequireDebugFalse'
#        }
#    },
#    'handlers': {
#        'mail_admins': {
#            'level': 'ERROR',
#            'filters': ['require_debug_false'],
#            'class': 'django.utils.log.AdminEmailHandler'
#        }
#   },
#    'loggers': {
#        'django.request': {
#            'handlers': ['mail_admins'],
#            'level': 'ERROR',
#            'propagate': True,
#        },
#    }
# }


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# END LOGGING CONFIGURATION


# WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
# END WSGI CONFIGURATION

# CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap', 'uni_form', 'bootstrap3', 'bootstrap4', 'materialize_css_forms', )
CRISPY_TEMPLATE_PACK = 'bootstrap3'


# Report Builder
# REPORT_BUILDER_INCLUDE = []
# REPORT_BUILDER_EXCLUDE =
#   ['user','groups','read','template','silo','readtoken']
# REPORT_BUILDER_ASYNC_REPORT = False

# wysiwyg settings
DJANGO_WYSIWYG_FLAVOR = "ckeditor"
CKEDITOR_UPLOAD_PATH = "media/uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 300,
    },
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

GOOGLE_ANALYTICS_PROPERTY_ID = None  # replaced in private settings file
GOOGLE_ANALYTICS_DOMAIN = 'example.org'  # replaced in private settings file

MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocationName", "london"),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'uk'}}),
        ("markerFitZoom", 12),
    ),
    "GOOGLE_MAP_API_KEY": os.environ.get('GOOGLE_MAP_API_KEY')
}


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET =  os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

# header setting for is_secure method on request object behavior control
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
