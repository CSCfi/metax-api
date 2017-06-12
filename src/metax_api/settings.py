"""
Django settings for metax_api project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import logging.config
import os
import yaml

if not os.getenv('TRAVIS', None):
    with open('/home/metax-user/app_config') as app_config:
        app_config_dict = yaml.load(app_config)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if os.getenv('TRAVIS', None):
    SECRET_KEY = '^pqn=v2i)%!w1oh=r!m_=wo_#w3)(@-#8%q_8&9z@slu+#q3+b'
else:
    SECRET_KEY = app_config_dict['django_secret_key']

# Consider enabling these
#CSRF_COOKIE_SECURE = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv('TRAVIS', None):
    DEBUG = True
else:
    DEBUG = app_config_dict['debug']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'metax_api',
    'rest_framework',
    'rest_framework_swagger',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ['rest_framework.renderers.JSONRenderer']

ROOT_URLCONF = 'metax_api.urls'

APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'metax_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

"""
The following uses the 'TRAVIS' (== True) environment variable on Travis
to detect the session, and changes the default database accordingly.
"""
if os.getenv('TRAVIS', None):
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'metax_db_test',
            'USER':     'metax_test',
            'PASSWORD': '',
            'HOST':     'localhost'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': app_config_dict['metax_database'],
            'USER': app_config_dict['metax_database_user'],
            'PASSWORD': app_config_dict['metax_database_password'],
            'HOST': app_config_dict['metax_database_host'],
            'PORT': '',
            'ATOMIC_REQUESTS': True
        }
    }

"""
Colorize automated test console output
"""
RAINBOWTESTS_HIGHLIGHT_PATH = BASE_DIR
TEST_RUNNER = 'rainbowtests.test.runner.RainbowDiscoverRunner'

"""
Logging rules:
- Django DEBUG enabled: Print everything from logging level DEBUG and up, to
both console, and log file.
- Django DEBUG disabled: Print everything from logging level INFO and up, only
to log file.
"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(name)s %(levelname)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/metax-api/metax_api.log',
            'formatter': 'standard',
            'filters': ['require_debug_true'],
        },
        'general': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/metax-api/metax_api.log',
            'formatter': 'standard',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['general', 'console', 'debug'],
        },
        'metax_api': {
            'handlers': ['general', 'console', 'debug'],
        }
    }
}

logger = logging.getLogger('metax_api')
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'Europe/Helsinki'

# A boolean that specifies whether Django’s translation system should
# be enabled. This provides an easy way to turn it off, for performance.
# If this is set to False, Django will make some optimizations so as not
# to load the translation machinery.
USE_I18N = True

# A boolean that specifies if localized formatting of data will
# be enabled by default or not. If this is set to True,
# e.g. Django will display numbers and dates using the format
# of the current locale.
USE_L10N = False

# A boolean that specifies if datetimes will be timezone-aware by default
# or not. If this is set to True, Django will use timezone-aware datetimes
# internally. Otherwise, Django will use naive datetimes in local time.
USE_TZ = False

DATETIME_INPUT_FORMATS = ['%Y-%m-%dT%H:%M:%S.%fZ']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# same dir as manage.py
STATIC_ROOT = os.path.join(os.path.dirname(PROJECT_DIR), 'static')
STATIC_URL = '/static/'


# Redis Cache
# https://www.peterbe.com/plog/fastest-redis-optimization-for-django
# Currently using this (pip: django-redis-cache): https://github.com/sebleier/django-redis-cache
# Consider alternatively pip:django-redis: https://github.com/niwinz/django-redis
CACHES = {
    'default': {
        'BACKEND': "redis_cache.RedisCache",
        'LOCATION': "/run/redis/redis.sock",
        'OPTIONS': {
            'DB': 1,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SERIALIZER_CLASS': 'redis_cache.serializers.MSGPackSerializer',
            'COMPRESSOR_CLASS': 'redis_cache.compressors.ZLibCompressor'
        }
    }
}
