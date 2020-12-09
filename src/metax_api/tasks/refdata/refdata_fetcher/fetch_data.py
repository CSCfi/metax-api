# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import logging.config

from metax_api.settings import env
from .domain.indexable_data import IndexableData
from .domain.reference_data import ReferenceData
from .service.finto_data_service import FintoDataService
from .service.local_data_service import LocalDataService
from .service.mime_data_service import MimeDataService
from .service.organization_service import OrganizationService

_logger = logging.getLogger(__name__)
REPO = env("REFDATA_REPO")


def write_to_file(ref_type, data):
    '''
    File for writing data to git repository.
    '''

    with open(f"{REPO}{ref_type}.es_ref", 'w') as gitfile:
        for ref in data:
            gitfile.write(str(ref) + '\n')
        _logger.info(f"Written {ref_type} to {REPO}{ref_type}.es_ref")

def fetch_data():

    # if len(sys.argv) < 2:
    #     _logger.error('Please provide path to reference data repository')
    #     sys.exit(1)

    finto_service = FintoDataService()
    local_service = LocalDataService()
    org_service = OrganizationService()
    mime_service = MimeDataService()

    # get for Finto data
    for data_type in ReferenceData.FINTO_REF_DATA_TYPES:
        finto_data_models = finto_service.get_data(data_type)
        if len(finto_data_models) == 0:
            _logger.info(f"No data models to get for finto data type {data_type}")
            continue
        else:
            _logger.info(f"Getting FINTO data: finto_{data_type}")
            write_to_file('finto_' + data_type, finto_data_models)

    # get local data
    for data_type in ReferenceData.LOCAL_REF_DATA_TYPES:
        local_data_models = local_service.get_data(data_type)
        if len(local_data_models) == 0:
            _logger.info(f"No data models to get for local data type {data_type}")
        else:
            _logger.info(f"Getting LOCAL data: local_{data_type}")
            write_to_file('local_' + data_type, local_data_models)

    # get organizations
    data_type = IndexableData.DATA_TYPE_ORGANIZATION
    org_data_models = org_service.get_data()
    if len(org_data_models) == 0:
        _logger.info("No data models to get for organizational data")
    else:
        _logger.info("Getting ORG data")
        write_to_file('org_' + data_type, org_data_models)

    # get mime types
    data_type = ReferenceData.DATA_TYPE_MIME_TYPE
    mime_data_models = mime_service.get_data()
    if len(mime_data_models) == 0:
        _logger.info("No data models to reindex for mime type data type")
    else:
        _logger.info("Getting MIME data")
        write_to_file('mime_' + data_type, mime_data_models)
