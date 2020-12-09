from metax_api.settings import env

# FYI
# REFDATA_GIT = 'git@ithub.com:CSCfi/metax-refdata.git'
REFDATA_REPO = env("REFDATA_REPO")
LOCAL_REF_DATA_FOLDER = env("LOCAL_REF_DATA_FOLDER")
ORG_FILE_PATH = env("ORG_FILE_PATH")
WKT_FILENAME = env("WKT_FILENAME")
ES_CONFIG_DIR = env("ES_CONFIG_DIR")