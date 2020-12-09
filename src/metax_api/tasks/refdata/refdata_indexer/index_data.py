# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import logging

from metax_api.settings import env
import metax_api.tasks.refdata.refdata_indexer.domain.datatypes as types
from metax_api.tasks.refdata.refdata_indexer.service.elasticsearch_service import ElasticSearchService

_logger = logging.getLogger(__name__)
es = ElasticSearchService()


def _delete_and_update_indexable_data(refdata_path, data_type):
    """
    Wrapper to call elasticsearch service with correct parameters.
    Determines filename and index for given data_type and calls the service.
    """
    if data_type in types.FINTO_TYPES:
        ref_type = 'finto'
    elif data_type in types.LOCAL_TYPES:
        ref_type = 'local'
    elif data_type in types.MIME_TYPE:
        ref_type = 'mime'
    elif data_type in types.ORG_TYPE:
        ref_type = 'org'

    if data_type in types.REFDATA_TYPES:
        index = 'reference_data'
    elif data_type in types.ORGDATA_TYPES:
        index = 'organization_data'

    _logger.info(f"Reading data {data_type}")

    try:
        with open('{}/{}_{}.es_ref'.format(refdata_path, ref_type, data_type), 'r') as f:
            indexable_data_list = f.readlines()

        _logger.info(f'Data for {data_type} loaded successfully' )
        es.delete_and_update_indexable_data(index, data_type, indexable_data_list)

    except FileNotFoundError as e:
        _logger.error(f"{e}")
        _logger.info(f"No data to reindex for {ref_type} data type {data_type}")
        pass

def index_data():
    # This is here for historical reasons and FYI describing feature of specifying indices for reindexing:

    # Runner file for indexing data to elasticsearch. Make sure requirements.txt is installed via pip.

    # params:
    #     indices_to_recreate (required):
    #         Comma separated list of indices that are recreated before indexing. Can also take
    #         value 'all' when all the indexes are recreated and 'no' when no indexes are recreated.

    #     types_to_reindex (required):
    #         Comma separated list of all types that are indexed.
    #         Ingests also values 'all', 'no' or the name of an index. If index name is given,
    #         all the types in that index are reindexed.

    ALL = 'all'

    refdata_path = env('REFDATA_REPO')
    indices_to_recreate = ['all']
    types_to_reindex = ['all']

    if any(i in [ALL, es.REF_DATA_INDEX_NAME] for i in indices_to_recreate):
        es.delete_index(es.REF_DATA_INDEX_NAME)

    if any(i in [ALL, es.ORG_DATA_INDEX_NAME] for i in indices_to_recreate):
        es.delete_index(es.ORG_DATA_INDEX_NAME)

    # Create reference data index with mappings
    if not es.index_exists(es.REF_DATA_INDEX_NAME):
        _logger.info('no existing REF_DATA index, creating.....')
        es.create_index(es.REF_DATA_INDEX_NAME, es.REF_DATA_INDEX_FILENAME)

    # Create organization data index with mappings
    if not es.index_exists(es.ORG_DATA_INDEX_NAME):
        _logger.info('no existing ORG_DATA index, creating.....')
        es.create_index(es.ORG_DATA_INDEX_NAME, es.ORG_DATA_INDEX_FILENAME)

    reindexed_types = set()

    if 'all' in types_to_reindex:
        reindexed_types.update(types.ALL_TYPES)
        types_to_reindex.remove('all')

    if es.REF_DATA_INDEX_NAME in types_to_reindex:
        reindexed_types.update(types.REFDATA_TYPES)
        types_to_reindex.remove(es.REF_DATA_INDEX_NAME)

    if es.ORG_DATA_INDEX_NAME in types_to_reindex:
        reindexed_types.update(types.ORGDATA_TYPES)
        types_to_reindex.remove(es.ORG_DATA_INDEX_NAME)

    reindexed_types.update(types_to_reindex)

    for type in reindexed_types:
        _delete_and_update_indexable_data(refdata_path, type)
    print('done!!!!!!!!!!')
    _logger.info("Done")
