# SPDX-FileCopyrightText: Copyright (c) 2018-2020 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later


FINTO_TYPES = [
    'field_of_science',
    'keyword',
    'language',
    'location'
]

LOCAL_TYPES = [
    'access_type',
    'contributor_role',
    'contributor_type',
    'event_outcome',
    'file_format_version',
    'file_type',
    'funder_type',
    'identifier_type',
    'license',
    'lifecycle_event',
    'preservation_event',
    'relation_type',
    'research_infra',
    'resource_type',
    'restriction_grounds',
    'use_category'
]

MIME_TYPE = 'mime_type'

ORG_TYPE = 'organization'

REFDATA_TYPES = FINTO_TYPES + LOCAL_TYPES + [MIME_TYPE]
ORGDATA_TYPES = [ORG_TYPE]

ALL_TYPES = REFDATA_TYPES + ORGDATA_TYPES
