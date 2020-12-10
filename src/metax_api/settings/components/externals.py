from metax_api.settings import env
from metax_api.settings.components.common import (
    IDA_DATA_CATALOG_IDENTIFIER,
    ATT_DATA_CATALOG_IDENTIFIER,
)

OAI = {
    "BASE_URL": env("OAI_BASE_URL"),
    "BATCH_SIZE": 25,
    "REPOSITORY_NAME": "Metax",
    "ETSIN_URL_TEMPLATE": "http://etsin.something.fi/dataset/%s",
    "ADMIN_EMAIL": "noreply@csc.fi",
    "SET_MAPPINGS": {
        "datasets": [IDA_DATA_CATALOG_IDENTIFIER, ATT_DATA_CATALOG_IDENTIFIER],
        "ida_datasets": [IDA_DATA_CATALOG_IDENTIFIER],
        "att_datasets": [ATT_DATA_CATALOG_IDENTIFIER],
    },
}
DATACITE = {
    "USERNAME": env("DATACITE_USERNAME"),
    "PASSWORD": env("DATACITE_PASSWORD"),
    "ETSIN_URL_TEMPLATE": env("DATACITE_ETSIN_URL_TEMPLATE"),
    "PREFIX": env("DATACITE_PREFIX"),
    "URL": env("DATACITE_URL"),
}
ORG_FILE_PATH = env("ORG_FILE_PATH")
WKT_FILENAME = env("WKT_FILENAME")
LOCAL_REF_DATA_FOLDER = env("LOCAL_REF_DATA_FOLDER")
