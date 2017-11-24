from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone
from metax_api.models import CatalogRecord
from metax_api.tests.utils import test_data_file_path, TestClassUtils
from pytz import timezone as tz
from rest_framework import status
from rest_framework.test import APITestCase


class CatalogRecordApiReadCommon(APITestCase, TestClassUtils):

    @classmethod
    def setUpClass(cls):
        """
        Loaded only once for test cases inside this class.
        """
        call_command('loaddata', test_data_file_path, verbosity=0)
        super(CatalogRecordApiReadCommon, cls).setUpClass()

    def setUp(self):
        self.catalog_record_from_test_data = self._get_object_from_test_data('catalogrecord', requested_index=0)
        self.pk = self.catalog_record_from_test_data['id']
        self.urn_identifier = self.catalog_record_from_test_data['research_dataset']['urn_identifier']


class CatalogRecordApiReadBasicTests(CatalogRecordApiReadCommon):

    """
    Basic read operations
    """

    def test_read_catalog_record_list(self):
        response = self.client.get('/rest/datasets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_catalog_record_details_by_pk(self):
        response = self.client.get('/rest/datasets/%s' % self.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['research_dataset']['urn_identifier'], self.urn_identifier)

    def test_read_catalog_record_details_by_identifier(self):
        response = self.client.get('/rest/datasets/%s' % self.urn_identifier)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['research_dataset']['urn_identifier'], self.urn_identifier)

    def test_read_catalog_record_details_not_found(self):
        response = self.client.get('/rest/datasets/shouldnotexist')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_catalog_record_exists(self):
        response = self.client.get('/rest/datasets/%s/exists' % self.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)
        response = self.client.get('/rest/datasets/%s/exists' % self.urn_identifier)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)
        response = self.client.get('/rest/datasets/%s/exists' % self.urn_identifier)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_read_catalog_record_does_not_exist(self):
        response = self.client.get('/rest/datasets/%s/exists' % 'urn:nbn:fi:non_existing_dataset_identifier')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_read_catalog_record_urn_identifiers(self):
        response = self.client.get('/rest/datasets/urn_identifiers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(response.data[0].startswith('pid:'))


class CatalogRecordApiReadPaginationTests(CatalogRecordApiReadCommon):

    """
    pagination
    """

    def test_read_catalog_record_list_pagination_1(self):
        response = self.client.get('/rest/datasets?limit=2&offset=0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2, 'There should have been exactly two results')
        self.assertEqual(response.data['results'][0]['id'], 1, 'Id of first result should have been 1')

    def test_read_catalog_record_list_pagination_2(self):
        response = self.client.get('/rest/datasets?limit=2&offset=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2, 'There should have been exactly two results')
        self.assertEqual(response.data['results'][0]['id'], 3, 'Id of first result should have been 3')


class CatalogRecordApiReadPreservationStateTests(CatalogRecordApiReadCommon):

    """
    preservation_state filtering
    """

    def test_read_catalog_record_search_by_preservation_state_0(self):
        response = self.client.get('/rest/datasets?state=0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data) > 2, True, 'There should have been multiple results for state=0 request')
        self.assertEqual(response.data['results'][0]['id'], 1)

    def test_read_catalog_record_search_by_preservation_state_1(self):
        response = self.client.get('/rest/datasets?state=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['results'][0]['id'], 2)

    def test_read_catalog_record_search_by_preservation_state_2(self):
        response = self.client.get('/rest/datasets?state=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['results'][0]['id'], 3)

    def test_read_catalog_record_search_by_preservation_state_666(self):
        response = self.client.get('/rest/datasets?state=666')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_read_catalog_record_search_by_preservation_state_many(self):
        response = self.client.get('/rest/datasets?state=1,2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['preservation_state'], 1)
        self.assertEqual(response.data['results'][1]['preservation_state'], 2)

    def test_read_catalog_record_search_by_preservation_state_invalid_value(self):
        response = self.client.get('/rest/datasets?state=1,a')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('is not an integer' in response.data['state'][0], True, 'Error should say letter a is not an integer')


class CatalogRecordApiReadQueryParamsTests(CatalogRecordApiReadCommon):

    """
    query_params filtering
    """

    def test_read_catalog_record_search_by_curator_1(self):
        response = self.client.get('/rest/datasets?curator=id:of:curator:rahikainen')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['results'][0]['research_dataset']['curator'][0]['name'], 'Rahikainen', 'Curator name is not matching')
        self.assertEqual(response.data['results'][4]['research_dataset']['curator'][0]['name'], 'Rahikainen', 'Curator name is not matching')

    def test_read_catalog_record_search_by_curator_2(self):
        response = self.client.get('/rest/datasets?curator=id:of:curator:jarski')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['results'][0]['research_dataset']['curator'][0]['name'], 'Jarski', 'Curator name is not matching')
        self.assertEqual(response.data['results'][3]['research_dataset']['curator'][0]['name'], 'Jarski', 'Curator name is not matching')

    def test_read_catalog_record_search_by_curator_not_found_1(self):
        response = self.client.get('/rest/datasets?curator=Not Found')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_read_catalog_record_search_by_curator_not_found_case_sensitivity(self):
        response = self.client.get('/rest/datasets?curator=id:of:curator:Rahikainen')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_read_catalog_record_search_by_curator_and_state_1(self):
        response = self.client.get('/rest/datasets?curator=id:of:curator:rahikainen&state=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], 2)
        self.assertEqual(response.data['results'][0]['preservation_state'], 1)
        self.assertEqual(response.data['results'][0]['research_dataset']['curator'][0]['name'], 'Rahikainen', 'Curator name is not matching')

    def test_read_catalog_record_search_by_curator_and_state_2(self):
        response = self.client.get('/rest/datasets?curator=id:of:curator:rahikainen&state=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], 3)
        self.assertEqual(response.data['results'][0]['preservation_state'], 2)
        self.assertEqual(response.data['results'][0]['research_dataset']['curator'][0]['name'], 'Rahikainen', 'Curator name is not matching')

    def test_read_catalog_record_search_by_curator_and_state_not_found(self):
        response = self.client.get('/rest/datasets?curator=id:of:curator:rahikainen&state=55')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_read_catalog_record_search_by_owner_id(self):
        cr = CatalogRecord.objects.get(pk=1)
        cr.owner_id = '123'
        cr.save()
        response = self.client.get('/rest/datasets?owner_id=123')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['owner_id'], '123')

    def test_read_catalog_record_search_by_creator_id(self):
        cr = CatalogRecord.objects.get(pk=1)
        cr.created_by_user_id = '123'
        cr.save()
        response = self.client.get('/rest/datasets?created_by_user_id=123')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['created_by_user_id'], '123')


class CatalogRecordApiReadXMLTransformationTests(CatalogRecordApiReadCommon):
    """
    dataset xml transformations
    """

    def test_read_dataset_xml_format_metax(self):
        response = self.client.get('/rest/datasets/1?dataset_format=metax')
        self._check_dataset_xml_format_response(response, '<researchdataset>')

    def test_read_dataset_xml_format_datacite(self):
        response = self.client.get('/rest/datasets/1?dataset_format=datacite')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_dataset_xml_format_response(response, '<resource>')

    def test_read_dataset_xml_format_error_unknown_format(self):
        response = self.client.get('/rest/datasets/1?dataset_format=doesnotexist')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _check_dataset_xml_format_response(self, response, element_name):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('content-type' in response._headers, True, response._headers)
        self.assertEqual('application/xml' in response._headers['content-type'][1], True, response._headers)
        self.assertEqual('<?xml version' in response.data[:20], True, response.data)
        self.assertEqual(element_name in response.data[:60], True, response.data)


class CatalogRecordApiReadHTTPHeaderTests(CatalogRecordApiReadCommon):
    #
    # header if-modified-since tests, single
    #

    # If the value of the timestamp given in the header is equal or greater than the value of modified_by_api field,
    # 404 should be returned since nothing has been modified. If the value of the timestamp given in the header is
    # less than value of modified_by_api field, the object should be returned since it means the object has been
    # modified after the header timestamp

    def test_get_with_if_modified_since_header_ok(self):
        cr = CatalogRecord.objects.get(pk=self.pk)
        modified_by_api = cr.modified_by_api
        modified_by_api_in_gmt = timezone.localtime(modified_by_api, timezone=tz('GMT'))

        if_modified_since_header_value = modified_by_api_in_gmt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/%s' % self.urn_identifier, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        if_modified_since_header_value = (modified_by_api_in_gmt + timedelta(seconds=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/%s' % self.urn_identifier, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        if_modified_since_header_value = (modified_by_api_in_gmt - timedelta(seconds=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/%s' % self.urn_identifier, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_with_if_modified_since_header_syntax_error(self):
        cr = CatalogRecord.objects.get(pk=self.pk)
        modified_by_api = cr.modified_by_api
        modified_by_api_in_gmt = timezone.localtime(modified_by_api, timezone=tz('GMT'))

        if_modified_since_header_value = modified_by_api_in_gmt.strftime('%a, %d %b %Y %H:%M:%S UTC')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/%s' % self.urn_identifier, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #
    # header if-modified-since tests, list
    #

    # List operation returns always 200 even if no datasets match the if-modified-since criterium

    def test_list_get_with_if_modified_since_header_ok(self):
        cr = CatalogRecord.objects.get(pk=self.pk)
        modified_by_api = cr.modified_by_api
        modified_by_api_in_gmt = timezone.localtime(modified_by_api, timezone=tz('GMT'))

        if_modified_since_header_value = modified_by_api_in_gmt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets?limit=100', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data.get('results')) == 2)

        if_modified_since_header_value = (modified_by_api_in_gmt + timedelta(seconds=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets?limit=100', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data.get('results')) == 2)

        # The asserts below may brake if the modified_by_api timestamps or the amount of test data objects are altered
        # in the test data

        if_modified_since_header_value = (modified_by_api_in_gmt - timedelta(seconds=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets?limit=100', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data.get('results')) > 2)
        self.assertTrue(len(response.data.get('results')) == 14)

    #
    # header if-modified-since tests, urn_identifiers
    #

    def test_urn_identifiers_get_with_if_modified_since_header_ok(self):
        cr = CatalogRecord.objects.get(pk=self.pk)
        modified_by_api = cr.modified_by_api
        modified_by_api_in_gmt = timezone.localtime(modified_by_api, timezone=tz('GMT'))

        if_modified_since_header_value = modified_by_api_in_gmt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/urn_identifiers', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) == 2)

        if_modified_since_header_value = (modified_by_api_in_gmt + timedelta(seconds=1)).strftime(
            '%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/urn_identifiers', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) == 2)

        # The assert below may brake if the modified_by_api timestamps or the amount of test data objects are altered
        # in the test data

        if_modified_since_header_value = (modified_by_api_in_gmt - timedelta(seconds=1)).strftime(
            '%a, %d %b %Y %H:%M:%S GMT')
        headers = {'HTTP_IF_MODIFIED_SINCE': if_modified_since_header_value}
        response = self.client.get('/rest/datasets/urn_identifiers', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 2)
