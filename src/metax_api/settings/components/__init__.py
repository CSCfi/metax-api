from pathlib import PurePath
from os.path import join

BASE_DIR = PurePath(__file__).parent.parent.parent.parent
REFDATA_PATH = join(BASE_DIR, "metax_api", "tasks", "refdata")
REFDATA_INDEXER_PATH = join(REFDATA_PATH, "refdata_indexer")
REFDATA_FETCHER_PATH = join(REFDATA_PATH, "refdata_fetcher")
