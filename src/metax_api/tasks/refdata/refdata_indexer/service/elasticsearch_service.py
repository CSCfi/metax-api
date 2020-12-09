# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import logging

from django.conf import settings
from elasticsearch import Elasticsearch

_logger = logging.getLogger('refdata')


class ElasticSearchService:
    '''
    Service for operating with Elasticsearch APIs. Used when data indices are created/deleted and
    data is deleted/reindexed.
    '''

    ES_CONFIG_DIR = settings.ES_CONFIG_DIR # env("ES_CONFIG_DIR") # 'resources/es-config/'

    REF_DATA_INDEX_NAME = 'reference_data'
    REF_DATA_INDEX_FILENAME = ES_CONFIG_DIR + 'reference_data_index.json'

    ORG_DATA_INDEX_NAME = 'organization_data'
    ORG_DATA_INDEX_FILENAME = ES_CONFIG_DIR + 'organization_data_index.json'

    def __init__(self):
        self.es = Elasticsearch(settings.ELASTICSEARCH["HOSTS"])

    def index_exists(self, index):
        return self.es.indices.exists(index=index)

    def create_index(self, index, filename):
        _logger.info(f"Trying to create index {index}")
        self.es.indices.create(index=index, body=self._get_json_file_as_str(filename))

    def delete_index(self, index):
        _logger.info(f"Trying to delete index {index}")
        self.es.indices.delete(index=index, ignore=[404])

    def delete_and_update_indexable_data(self, index, doc_type, indexable_data_list):
        if len(indexable_data_list) > 0:
            bulk_update_str = "\n".join(
                map(
                    lambda idx_data:
                    self._create_bulk_update_row_for_indexable_data(index, idx_data),
                    indexable_data_list)
            )
            self._delete_all_documents_from_index_with_type(index, doc_type)
            _logger.info(f"Trying to bulk update reference data with type {doc_type} to index {index}")

            self.es.bulk(body=bulk_update_str, request_timeout=30)

        else:
            _logger.info(f"No data for {doc_type}")

    def _delete_all_documents_from_index_with_type(self, index, doc_type):
        _logger.info(f"Trying to delete all documents from index {index} having type {doc_type}")
        self.es.delete_by_query(index=index, body="{\"query\": { \"match\": {\"type\": \"%s\"}}}" % doc_type)

    def _create_bulk_update_row_for_indexable_data(self, index, indexable_data_item):
        return "{\"index\":{\"_index\": \"" + index + "\"}}\n" + indexable_data_item

    def _create_bulk_delete_row_indexable_data(self, index, indexable_data_item):
        return "{\"delete\":{\"_index\": \"" + \
            index + "\", \"_id\":\"" + \
            indexable_data_item.get_es_document_id() + "\"}}"

    def _get_json_file_as_str(self, filename):
        with open(filename) as json_data:
            return json.load(json_data)
