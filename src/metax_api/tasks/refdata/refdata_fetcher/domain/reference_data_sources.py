# SPDX-FileCopyrightText: Copyright (c) 2018-2020 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later

from metax_api.tasks.refdata.refdata_fetcher.domain.reference_data import ReferenceData

FINTO_REFERENCE_DATA_SOURCE_URLS = {
    ReferenceData.DATA_TYPE_FIELD_OF_SCIENCE: 'http://finto.fi/rest/v1/okm-tieteenala/data',
    ReferenceData.DATA_TYPE_LANGUAGE: 'http://finto.fi/rest/v1/lexvo/data',
    ReferenceData.DATA_TYPE_LOCATION: 'http://finto.fi/rest/v1/yso-paikat/data',
    ReferenceData.DATA_TYPE_KEYWORD: 'http://finto.fi/rest/v1/koko/data'
}

WKT_FILENAME = 'metax_api/tasks/refdata/refdata_fetcher/resources/uri_to_wkt.json'

INFRA_REF_DATA_SOURCE_URL = 'https://avaa.tdata.fi/api/jsonws/tupa-portlet.Infrastructures/get-all-infrastructures'

LOCAL_REFDATA_FOLDER = 'metax_api/tasks/refdata/refdata_fetcher/resources/local-refdata/'

MIME_TYPE_REF_DATA_SOURCE_URL = 'https://www.iana.org/assignments/media-types/media-types.xml'

ORG_TYPE_INPUT_FILES = ['metax_api/tasks/refdata/refdata_fetcher/resources/organizations/organizations.csv']
