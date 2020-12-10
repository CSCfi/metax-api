"""
This is a django-split-settings main file.
For more information read this:
https://github.com/sobolevn/django-split-settings
To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""
from os.path import join

import environ
from icecream import ic
from split_settings.tools import include

from metax_api.settings.components import BASE_DIR  # src

# Managing environment via DJANGO_ENV variable:
REFDATA_INDEXER_PATH = join(
    BASE_DIR, "metax_api", "tasks", "refdata", "refdata_indexer"
)
env = environ.Env(
    # set casting, default value
    ADDITIONAL_USER_PROJECTS_PATH=(str, ""),
    DEBUG=(bool, False),
    DJANGO_ENV=(str, "local"),
    ELASTIC_SEARCH_PORT=(int, 9200),
    ERROR_FILES_PATH=(str, join(BASE_DIR, "log", "errors")),
    ES_CONFIG_DIR=(str, join(REFDATA_INDEXER_PATH, "resources", "es-config/")),
    LOCAL_REF_DATA_FOLDER=(
        str,
        join(REFDATA_INDEXER_PATH, "resources", "local-refdata/"),
    ),
    LOGGING_DEBUG_HANDLER_FILE=(str, join(BASE_DIR, "log", "metax_api.log")),
    LOGGING_GENERAL_HANDLER_FILE=(str, join(BASE_DIR, "log", "metax_api.log")),
    LOGGING_JSON_FILE_HANDLER_FILE=(str, join(BASE_DIR, "log", "metax_api.json.log")),
    METAX_ENV=(str, "local_development"),
    METAX_DATABASE_PORT=(str, 5432),
    ORG_FILE_PATH=(
        str,
        join(REFDATA_INDEXER_PATH, "resources", "organizations", "organizations.csv"),
    ),
    RABBIT_MQ_PORT=(int, 5672),
    REDIS_HOST=(str, "localhost"),
    REDIS_PORT=(int, 6379),
    TRAVIS=(bool, False),
    WKT_FILENAME=(str, join(REFDATA_INDEXER_PATH, "resources", "uri_to_wkt.json")),
)
# reading .env file
environ.Env.read_env()

ENV = env("DJANGO_ENV")

base_settings = [
    "components/common.py",
    "components/logging.py",
    "components/redis.py",
    "components/access_control.py",
    "components/elasticsearch.py",
    "components/rabbitmq.py",
    "components/externals.py",
    "environments/{0}.py".format(ENV),
    # Optionally override some settings:
    # optional('environments/legacy.py'),
]
ic(ENV)

# Include settings:
include(*base_settings)
