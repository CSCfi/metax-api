# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

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
import time

import yaml

from metax_api.utils import executing_test_case, executing_travis

executing_in_travis = executing_travis()
executing_in_test_case = executing_test_case()

if not executing_in_travis:
    with open('/home/metax-user/app_config') as app_config:
        app_config_dict = yaml.load(app_config)

    if 'METAX_ENV' in app_config_dict:
        METAX_ENV = app_config_dict['METAX_ENV']
    else:
        raise Exception('METAX_ENV missing from app_config')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if executing_in_travis:
    SECRET_KEY = '^pqn=v2i)%!w1oh=r!m_=wo_#w3)(@-#8%q_8&9z@slu+#q3+b'
else:
    SECRET_KEY = app_config_dict['DJANGO_SECRET_KEY']

if executing_in_test_case or executing_in_travis:
    # used by test cases and travis during test case execution to authenticate with certain api's
    API_TEST_USER = {
        'username': 'testuser',
        'password': 'testuserpassword'
    }
    API_METAX_USER = {
        'username': 'metax',
        'password': 'metaxpassword'
    }
    API_AUTH_TEST_USER = {
        'username': 'api_auth_user',
        'password': 'assword'
    }

    API_TEST_USERS = [
        API_TEST_USER,
        API_METAX_USER,
        API_AUTH_TEST_USER,
    ]

    API_ACCESS = {
        "rest": {
            "apierrors":    {
                "read": ["testuser", "metax"],
                "write": ["testuser", "metax"]
            },
            "contracts":    {
                "read": ["testuser", "metax"],
                "write": ["testuser", "metax"]
            },
            "datacatalogs": {
                "read": ["all"],
                "write": ["testuser", "metax"]
            },
            "datasets":     {
                "read": ["all"],
                "write": ["testuser", "metax", "api_auth_user", "endusers"]
            },
            "directories":  {
                "read": ["testuser", "metax", "endusers"],
                "write": ["testuser", "metax"]
            },
            "files":        {
                "read": ["testuser", "metax", "api_auth_user", "endusers"],
                "write": ["testuser", "metax"]
            },
            "filestorages": {
                "read": ["testuser", "metax"],
                "write": ["testuser", "metax"]
            },
            "schemas":      {
                "read": ["all"],
                "write": ["testuser", "metax"]
            }
        },
        "rpc": {
            "datasets": {
                "get_minimal_dataset_template": { "use": ["all"] }
            },
            "statistics": {
                "something": { "use": ["all"] }
            }
        }
    }
elif METAX_ENV == 'test':
    # in test-env, modify API_ACCESS to give read and write perms to all (public). note that
    # this affects only per-api access; nginx permissions still limits general write requests
    API_ACCESS = app_config_dict['API_ACCESS']

    for api, perms in API_ACCESS['rest'].items():
        if 'all' not in perms['read']:
            perms['read'].append('all')
        if 'all' not in perms['write']:
            perms['write'].append('all')
else:
    # localdev, stable, production
    API_ACCESS = app_config_dict['API_ACCESS']

if executing_in_travis:
    ALLOWED_AUTH_METHODS = ['Basic', 'Bearer']
else:
    # Basic for services, Bearer for end users. Disabling Bearer auth method disables end user access
    ALLOWED_AUTH_METHODS = app_config_dict['ALLOWED_AUTH_METHODS']

if executing_in_test_case or executing_in_travis:
    END_USER_ALLOWED_DATA_CATALOGS = [
        "urn:nbn:fi:att:data-catalog-ida",
        "urn:nbn:fi:att:data-catalog-att",
        "urn:nbn:fi:att:data-catalog-legacy",
    ]
    LEGACY_CATALOGS = [
        "urn:nbn:fi:att:data-catalog-legacy",
    ]
else:
    # allow end users to create catalogrecords only to the following data catalogs
    END_USER_ALLOWED_DATA_CATALOGS = [
        app_config_dict['IDA_DATACATALOG_IDENTIFIER'],
        app_config_dict['ATT_DATACATALOG_IDENTIFIER'],
        app_config_dict['LEGACY_DATACATALOG_IDENTIFIER'],
    ]

    # catalogs where uniqueness of dataset pids is not enforced.
    LEGACY_CATALOGS = [
        app_config_dict['LEGACY_DATACATALOG_IDENTIFIER'],
    ]

# endpoint in localhost where bearer tokens should be sent for validation
VALIDATE_TOKEN_URL = 'https://127.0.0.1/secure/validate_token'

if executing_in_test_case or executing_in_travis:
    ERROR_FILES_PATH = '/tmp/metax-api-tests/errors'
else:
    # location to store information about exceptions occurred during api requests
    ERROR_FILES_PATH = '/var/log/metax-api/errors'

# Consider enabling these
#CSRF_COOKIE_SECURE = True
#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True

# Allow only specific hosts to access the app
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
if not os.getenv('TRAVIS', None):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    for allowed_host in app_config_dict['ALLOWED_HOSTS']:
        ALLOWED_HOSTS.append(allowed_host)

# SECURITY WARNING: don't run with debug turned on in production!
if executing_in_travis:
    DEBUG = True
else:
    DEBUG = app_config_dict['DEBUG']

# when using the requests-library or similar, should be used to decide when to verify self-signed certs
TLS_VERIFY = False if DEBUG else True

# Application definition

AUTH_USER_MODEL = 'metax_api.MetaxUser'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'metax_api',
]

if DEBUG:
    INSTALLED_APPS.append('django.contrib.staticfiles')

MIDDLEWARE = [
    'metax_api.middleware.RequestLogging',
    # note: not strictly necessary if running in a private network
    # https://docs.djangoproject.com/en/1.11/ref/middleware/#module-django.middleware.security
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'metax_api.middleware.IdentifyApiCaller',
    'metax_api.middleware.AddLastModifiedHeaderToResponse',
    'metax_api.middleware.StreamHttpResponse',
]

if not (executing_in_test_case or executing_in_travis):
    # security settings
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.OrderingFilter'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}


REST_FRAMEWORK['DEFAULT_PARSER_CLASSES'] = [
    'rest_framework.parsers.JSONParser',
    'metax_api.parsers.XMLParser',
]

if DEBUG:
    # the renderer is selected based on the 'Accept' HTTP header
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'metax_api.renderers.XMLRenderer',
    ]
else:
    # the renderer is selected based on the 'Accept' HTTP header
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
        'metax_api.renderers.HTMLToJSONRenderer',
        'metax_api.renderers.XMLRenderer',
    ]


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
if executing_in_travis:
    DATABASES = {
        'default': {
            'NAME':     'metax_db_test',
            'USER':     'metax_test',
            'PASSWORD': '',
            'HOST':     'localhost',
        }
    }
else:
    DATABASES = {
        'default': {
            'NAME': app_config_dict['METAX_DATABASE'],
            'USER': app_config_dict['METAX_DATABASE_USER'],
            'PASSWORD': app_config_dict['METAX_DATABASE_PASSWORD'],
            'HOST': app_config_dict['METAX_DATABASE_HOST'],
            'PORT': '',
            # default is 0 == "reconnect to db on every request". placing setting here for visibility
            'CONN_MAX_AGE': 0,
        }
    }

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['ATOMIC_REQUESTS'] = True

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
            # timestamp, process id, python module name, loglevel, msg content...
            'format': '%(asctime)s p%(process)d %(name)s %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S.%03dZ',
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

logging.Formatter.converter = time.gmtime
logger = logging.getLogger('metax_api')
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

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
USE_TZ = True

DATETIME_INPUT_FORMATS = ['%Y-%m-%dT%H:%M:%S.%fZ']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# same dir as manage.py
STATIC_ROOT = os.path.join(os.path.dirname(PROJECT_DIR), 'static')
STATIC_URL = '/static/'

if not executing_in_travis:
    # settings for custom redis-py cache helper in utils/redis.py
    REDIS = {
        'PASSWORD': app_config_dict['REDIS']['PASSWORD'],
        'LOCALHOST_PORT': app_config_dict['REDIS']['LOCALHOST_PORT'],

        # https://github.com/andymccurdy/redis-py/issues/485#issuecomment-44555664
        'SOCKET_TIMEOUT': 0.1,

        # db index reserved for test suites
        'TEST_DB': app_config_dict['REDIS']['TEST_DB'],

        # enables extra logging to console during cache usage
        'DEBUG': False,

        'SENTINEL': {
            'HOSTS': app_config_dict['REDIS']['SENTINEL']['HOSTS'],
            'SERVICE': app_config_dict['REDIS']['SENTINEL']['SERVICE']
        }
    }

if executing_in_travis:
    ELASTICSEARCH = {
        'HOSTS': ['metax-test.csc.fi/es'],
        'USE_SSL': True,
        'ALWAYS_RELOAD_REFERENCE_DATA_ON_RESTART': True,
    }
else:
    ELASTICSEARCH = {
        'HOSTS': app_config_dict['ELASTICSEARCH']['HOSTS'],
        # normally cache is reloaded from elasticsearch only if reference data is missing.
        # for one-off reload / debugging / development, use below flag
        'ALWAYS_RELOAD_REFERENCE_DATA_ON_RESTART': app_config_dict['ALWAYS_RELOAD_REFERENCE_DATA_ON_RESTART'],
    }

if not executing_in_travis:
    RABBITMQ = {
        'HOSTS':    app_config_dict['RABBITMQ']['HOSTS'],
        'PORT':     app_config_dict['RABBITMQ']['PORT'],
        'USER':     app_config_dict['RABBITMQ']['USER'],
        'VHOST':    app_config_dict['RABBITMQ']['VHOST'],
        'PASSWORD': app_config_dict['RABBITMQ']['PASSWORD'],
        'EXCHANGES': [
            {
                'NAME': 'datasets',
                'TYPE': 'direct',
                # make rabbitmq remember queues after restarts
                'DURABLE': True
            }
        ]
    }

if executing_in_travis:
    OAI = {
        'BASE_URL': 'http://metax-test.csc.fi/oai/',
        'BATCH_SIZE': 25,
        'REPOSITORY_NAME': 'Metax',
        'ETSIN_URL_TEMPLATE': 'http://etsin.something.fi/dataset/%s',
        'ADMIN_EMAIL': 'noreply@csc.fi',
        'SET_MAPPINGS': {
            'datasets': [
                'urn:nbn:fi:att:data-catalog-ida',
                'urn:nbn:fi:att:data-catalog-att'
            ],
            'ida_datasets': [
                'urn:nbn:fi:att:data-catalog-ida'
            ],
            'att_datasets': [
                'urn:nbn:fi:att:data-catalog-att'
            ]
        }
    }
else:
    OAI = {
        'BASE_URL': app_config_dict['OAI']['BASE_URL'],
        'BATCH_SIZE': app_config_dict['OAI']['BATCH_SIZE'],
        'REPOSITORY_NAME': app_config_dict['OAI']['REPOSITORY_NAME'],
        'ETSIN_URL_TEMPLATE': app_config_dict['OAI']['ETSIN_URL_TEMPLATE'],
        'ADMIN_EMAIL': app_config_dict['OAI']['ADMIN_EMAIL'],
        'SET_MAPPINGS': app_config_dict['OAI']['SET_MAPPINGS']
    }

if executing_in_travis:
    DATACITE = {
        'USERNAME': 'datacite_user',
        'PASSWORD': 'datacite_password',
        'ETSIN_URL_TEMPLATE': 'https://etsin.something.fi/dataset/%s',
        'PREFIX': '10.5072'
    }
else:
    DATACITE = {
        'USERNAME': app_config_dict['DATACITE']['USERNAME'],
        'PASSWORD': app_config_dict['DATACITE']['PASSWORD'],
        'ETSIN_URL_TEMPLATE': app_config_dict['DATACITE']['ETSIN_URL_TEMPLATE'],
        'PREFIX': app_config_dict['DATACITE']['PREFIX']
    }