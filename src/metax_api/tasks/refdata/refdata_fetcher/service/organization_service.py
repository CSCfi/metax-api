# SPDX-FileCopyrightText: Copyright (c) 2018-2019 Ministry of Education and Culture, Finland
#
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os

from metax_api.tasks.refdata.refdata_fetcher.domain.organization_data import OrganizationData
import metax_api.tasks.refdata.refdata_fetcher.organization_csv_parser as org_parser


class OrganizationService:
    """
    Service for getting organization data for elasticsearch index
    """

    INPUT_FILE = org_parser.OUTPUT_FILE

    def get_data(self):
        # Parse csv files containing organizational data
        org_parser.parse_csv()

        index_data_models = []
        with open(self.INPUT_FILE) as org_data_file:
            data = json.load(org_data_file)

        for org in data:
            parent_id = org.get('parent_id', '')
            same_as = org.get('same_as', [])
            org_csc = org.get('org_csc', '')
            index_data_models.append(OrganizationData(org['org_id'], org['label'], parent_id, same_as, org_csc))

        index_data_models.sort(key=lambda x: x.code)

        os.remove(self.INPUT_FILE)
        return index_data_models
