# This file is part of the Metax API service
#
# Copyright 2017-2020 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

import responses
from django.conf import settings as django_settings
from rest_framework import status

from metax_api.models import (
    CatalogRecordV2,
    DataCatalog,
)
from metax_api.utils import get_tz_aware_now_without_micros
from metax_api.tests.utils import get_test_oidc_token
from .write import CatalogRecordApiWriteCommon


CR = CatalogRecordV2
END_USER_ALLOWED_DATA_CATALOGS = django_settings.END_USER_ALLOWED_DATA_CATALOGS


class CatalogRecordDraftTests(CatalogRecordApiWriteCommon):
    """
    Tests related to draft datasets
    """
    def setUp(self):
        super().setUp()

        # create catalogs with end user access permitted
        dc = DataCatalog.objects.get(pk=1)
        catalog_json = dc.catalog_json
        for identifier in END_USER_ALLOWED_DATA_CATALOGS:
            catalog_json['identifier'] = identifier
            dc = DataCatalog.objects.create(
                catalog_json=catalog_json,
                date_created=get_tz_aware_now_without_micros(),
                catalog_record_services_create='testuser,api_auth_user,metax',
                catalog_record_services_edit='testuser,api_auth_user,metax'
            )

        self.token = get_test_oidc_token(new_proxy=True)
        self._mock_token_validation_succeeds()
        # Create published record with owner: testuser and pk 1
        # Create draft records with owner: testuser, pk: 2 and owner: 'some owner who is not you', pk 3
        self._set_cr_owner_and_state(1, 'published', self.token['CSCUserName']) # Published dataset
        self.assertEqual(CatalogRecordV2.objects.get(pk=1).metadata_provider_user, 'testuser')

        self._set_cr_owner_and_state(2, 'draft', self.token['CSCUserName']) # testusers' draft
        self.assertEqual(CatalogRecordV2.objects.get(pk=2).metadata_provider_user, 'testuser')

        self._set_cr_owner_and_state(3, 'draft', '#### Some owner who is not you ####') # Draft dataset for some user
        self.assertNotEqual(CatalogRecordV2.objects.get(pk=3).metadata_provider_user, 'testuser')

    def _set_cr_owner_and_state(self, cr_id, state, owner):
        ''' helper method for testing user accessibility for draft datasets '''
        cr = CatalogRecordV2.objects.get(pk=cr_id)
        cr.state = state
        cr.user_created = owner
        cr.metadata_provider_user = owner
        cr.editor = None # pretend the record was created by user directly
        cr.data_catalog_id = DataCatalog.objects.get(catalog_json__identifier=END_USER_ALLOWED_DATA_CATALOGS[0]).id
        cr.force_save()

    def test_field_exists(self):
        """Try fetching any dataset, field 'state' should be returned'"""

        cr = self.client.get('/rest/v2/datasets/13').data
        self.assertEqual('state' in cr, True)

    def test_change_state_field_through_API(self):
        """Fetch a dataset and change its state.
        Value should remain: 'published' """

        cr = self.client.get('/rest/v2/datasets/1').data
        cr['state'] = 'changed value'
        response = self.client.put('/rest/v2/datasets/1', cr, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertFalse(response.data['state'] == 'changed value')

    ###
    # Tests for different user roles access to drafts
    ###

    @responses.activate
    def test_endusers_access_to_draft_datasets(self):
        ''' End user should get published data and his/her drafts '''
        # Test access as end user
        self._use_http_authorization(method='bearer', token=self.token)

        # Test access for owner of dataset
        response = self.client.get('/rest/v2/datasets/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.status_code)
        response = self.client.get('/rest/v2/datasets/2')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.status_code)
        response = self.client.get('/rest/v2/datasets/3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.status_code)
        # Test for multiple datasets
        response = self.client.get('/rest/v2/datasets', format="json")
        # Returned list of datasets should not have owner "#### Some owner who is not you ####"
        owners = [cr['metadata_provider_user'] for cr in response.data['results']]
        self.assertEqual('#### Some owner who is not you ####' not in owners, True, response.data)

    def test_service_users_access_to_draft_datasets(self):
        ''' Service users should get all data '''
        # test access as a service-user
        self._use_http_authorization(method='basic', username='metax')

        response = self.client.get('/rest/v2/datasets/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.status_code)
        response = self.client.get('/rest/v2/datasets/2')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.status_code)
        response = self.client.get('/rest/v2/datasets/3')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.status_code)
        # test for multiple datasets
        response = self.client.get('/rest/v2/datasets', format="json")
        # Returned list of datasets should have owner "#### Some owner who is not you ####"
        owners = [cr['metadata_provider_user'] for cr in response.data['results']]
        self.assertEqual('#### Some owner who is not you ####' in owners, True, response.data)

    def test_anonymous_users_access_to_draft_datasets(self):
        ''' Unauthenticated user should get only published datasets '''
        # Test access as unauthenticated user
        self.client._credentials = {}

        response = self.client.get('/rest/v2/datasets/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/rest/v2/datasets/2')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)
        response = self.client.get('/rest/v2/datasets/3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)
        # test for multiple datasets
        response = self.client.get('/rest/v2/datasets', format="json")
        # Returned list of datasets should not have drafts
        states = [cr['state'] for cr in response.data['results']]
        self.assertEqual('draft' not in states, True, response.data)

    ###
    # Tests for different user roles access to update drafts
    ###

    @responses.activate
    def test_endusers_can_update_draft_datasets(self):
        ''' End user should be able to update only his/her drafts '''
        # Set end user
        self._use_http_authorization(method='bearer', token=self.token)

        for http_verb in ['put', 'patch']:
            update_request = getattr(self.client, http_verb)
            data1 = self.client.get('/rest/v2/datasets/1').data # published
            response = update_request('/rest/v2/datasets/1', data1, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            data2 = self.client.get('/rest/v2/datasets/2').data # end users own draft
            response = update_request('/rest/v2/datasets/2', data2, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            data3 = self.client.get('/rest/v2/datasets/3').data # someone elses draft
            response = update_request('/rest/v2/datasets/3', data3, format="json")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

            # test for multiple datasets
            response = update_request('/rest/v2/datasets', [data1, data2, data3], format="json")
            owners = [cr['object']['metadata_provider_user'] for cr in response.data['success']]
            self.assertEqual('#### Some owner who is not you ####' not in owners, True, response.data)

    def test_service_users_can_update_draft_datasets(self):
        ''' Dataset drafts should be able to be updated by service users (service is responsible that
            their current user in e.g. Qvain is allowed to access the dataset)'''
        # Set service-user
        self._use_http_authorization(method='basic', username='metax')

        for http_verb in ['put', 'patch']:
            update_request = getattr(self.client, http_verb)
            data1 = self.client.get('/rest/v2/datasets/1').data # published
            response = update_request('/rest/v2/datasets/1', data1, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            data2 = self.client.get('/rest/v2/datasets/2').data # draft
            response = update_request('/rest/v2/datasets/2', data2, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            data3 = self.client.get('/rest/v2/datasets/3').data # draft
            response = update_request('/rest/v2/datasets/3', data3, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            # test for multiple datasets
            response = update_request('/rest/v2/datasets', [data1, data2, data3], format="json")
            self.assertEqual(len(response.data['success']), 3, 'response.data should contain 3 changed objects')
            owners = [cr['object']['metadata_provider_user'] for cr in response.data['success']]
            self.assertEqual('#### Some owner who is not you ####' in owners, True, response.data)

    def test_anonymous_user_cannot_update_draft_datasets(self):
        ''' Unauthenticated user should not be able to know drafts exists in the first place'''
        # Set unauthenticated user
        self.client._credentials = {}

        # Fetches a published dataset since unauthenticated user can't get drafts
        response = self.client.get('/rest/v2/datasets/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        data = response.data

        for http_verb in ['put', 'patch']:
            update_request = getattr(self.client, http_verb)
            response = update_request('/rest/v2/datasets/1', data, format="json") # published
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.status_code)
            response = update_request('/rest/v2/datasets/2', data, format="json") # draft
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.status_code)
            response = update_request('/rest/v2/datasets/3', data, format="json") # draft
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.status_code)

            # test for multiple datasets
            response = update_request('/rest/v2/datasets', data, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.status_code)

    ###
    # Tests for deleting drafts
    ###

    def test_draft_is_permanently_deleted_by_service_user(self):
        '''Draft datasets should be permanently deleted from the database.
        Only the dataset owner is able to delete draft datasets.'''
        # Set service-user
        self._use_http_authorization(method='basic', username='metax')

        for cr_id in (2, 3):
            response = self.client.delete('/rest/v2/datasets/%d' % cr_id)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
            self.assertFalse(CatalogRecordV2.objects_unfiltered.filter(pk=cr_id).exists())

    @responses.activate
    def test_draft_is_permanently_deleted_by_enduser(self):
        # Set end user
        self._use_http_authorization(method='bearer', token=self.token)

        response = self.client.delete('/rest/v2/datasets/2')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertFalse(CatalogRecordV2.objects_unfiltered.filter(pk=2).exists())
        response = self.client.delete('/rest/v2/datasets/3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    ###
    # Tests for saving drafts
    ###

    def test_service_users_can_save_draft_datasets(self):
        ''' Drafts should be saved without preferred identifier '''
        # test access as a service-user
        self._use_http_authorization(method='basic', username='metax')

        response = self.client.post('/rest/v2/datasets?draft', self.cr_test_data, format="json")

        pid = response.data['research_dataset']['preferred_identifier']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(pid == 'draft:%s' % response.data['identifier'], response.data)
        self.assertTrue('urn' not in pid, response.data)
        self.assertTrue('doi' not in pid, response.data)
        self.assertTrue(response.data['state'] == 'draft', response.data)

        for queryparam in ('', '?draft=false'):
            response = self.client.post('/rest/v2/datasets{}'.format(queryparam), self.cr_test_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
            self.assertTrue(response.data['state'] == 'published', response.data)


class CatalogRecordDraftsOfPublished(CatalogRecordApiWriteCommon):

    """
    Tests related to drafts of published records.
    """

    def _create_dataset(self, cumulative=False, draft=False, with_files=False):
        draft = 'true' if draft else 'false'
        cumulative_state = 1 if cumulative else 0

        self.cr_test_data['cumulative_state'] = cumulative_state

        if with_files is False:
            self.cr_test_data['research_dataset'].pop('files', None)
            self.cr_test_data['research_dataset'].pop('directories', None)

        response = self.client.post('/rest/v2/datasets?draft=%s' % draft, self.cr_test_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        return response.data

    def _create_draft(self, id):
        # create draft
        response = self.client.post('/rpc/v2/datasets/create_draft?identifier=%d' % id, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        draft_id = response.data['id']

        # retrieve draft data for modifications
        response = self.client.get('/rest/v2/datasets/%s' % draft_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('draft_of' in response.data, True, response.data)
        self.assertEqual(response.data['draft_of']['id'], id, response.data)

        return response.data

    def _merge_draft_changes(self, draft_id):
        response = self.client.post('/rpc/v2/datasets/merge_draft?identifier=%d' % draft_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # draft should be permanently destroyed
        draft_found = CR.objects_unfiltered.filter(pk=draft_id).exists()
        self.assertEqual(draft_found, False)

    def test_create_and_merge_draft(self):
        """
        A simple test to create a draft, change some metadata, and publish the changes.
        """
        cr = self._create_dataset()
        initial_title = cr['research_dataset']['title']

        # create draft
        draft_cr = self._create_draft(cr['id'])
        draft_cr['research_dataset']['title']['en'] = 'modified title'

        # ensure original now has a link to next_draft
        response = self.client.get('/rest/v2/datasets/%s' % cr['id'], format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('next_draft' in response.data, True, response.data)
        self.assertEqual(response.data['next_draft']['id'], draft_cr['id'], response.data)

        # update the draft
        response = self.client.put('/rest/v2/datasets/%d' % draft_cr['id'], draft_cr, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # ensure original dataset
        # - does not have the changes yet, since draft has not been published
        # - has next_draft link, pointing to the preciously created draft
        original_cr = CR.objects.get(pk=cr['id'])
        self.assertEqual(original_cr.research_dataset['title'], initial_title, original_cr.research_dataset['title'])
        self.assertEqual(original_cr.next_draft_id, draft_cr['id'])

        # merge draft changes back to original published dataset
        self._merge_draft_changes(draft_cr['id'])

        # changes should now reflect on original published dataset
        response = self.client.get('/rest/v2/datasets/%s' % cr['id'], format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.data['research_dataset']['title'],
            draft_cr['research_dataset']['title'],
            response.data
        )
        self.assertEqual('next_draft' in response.data, False, 'next_draft link should be gone')

    def test_add_files_to_draft_normal_dataset(self):
        """
        Test case where dataset has 0 files in the beginning.
        """
        cr = self._create_dataset(with_files=False)
        draft_cr = self._create_draft(cr['id'])

        # add file to draft
        file_changes = { 'files': [{ 'identifier': 'pid:urn:1' }]}
        response = self.client.post('/rest/v2/datasets/%d/files' % draft_cr['id'], file_changes, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # ensure original has no files
        self.assertEqual(CR.objects.get(pk=cr['id']).files.count(), 0)

        # merge draft changes back to original published dataset
        self._merge_draft_changes(draft_cr['id'])

        # ensure original now has the files
        self.assertEqual(CR.objects.get(pk=cr['id']).files.count(), 1)

    def test_add_files_to_draft_when_files_already_exist(self):
        """
        Dataset already has files, so only metadata changes should be allowed. Adding
        or removing files should be prevented.
        """
        cr = self._create_dataset(with_files=True)
        draft_cr = self._create_draft(cr['id'])

        # add file to draft
        file_changes = { 'files': [{ 'identifier': 'pid:urn:10' }]}
        response = self.client.post('/rest/v2/datasets/%d/files' % draft_cr['id'], file_changes, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_add_files_to_draft_cumulative_dataset(self):
        """
        Adding new files to cumulative draft should be ok. Removing files should be prevented.
        """
        cr = self._create_dataset(cumulative=True, with_files=True)
        draft_cr = self._create_draft(cr['id'])

        # try to remove a file. should be stopped
        file_changes = { 'files': [{ 'identifier': 'pid:urn:1', 'exclude': True }]}
        response = self.client.post('/rest/v2/datasets/%d/files' % draft_cr['id'], file_changes, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        # now add files
        file_changes = { 'files': [{ 'identifier': 'pid:urn:10' }]}
        response = self.client.post('/rest/v2/datasets/%d/files' % draft_cr['id'], file_changes, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # ensure original has no files YET
        self.assertEqual(CR.objects.get(pk=cr['id']).files.count(), 2)

        # merge draft changes back to original published dataset
        self._merge_draft_changes(draft_cr['id'])

        # ensure original now has the files
        self.assertEqual(CR.objects.get(pk=cr['id']).files.count(), 3)

    def test_delete_draft(self):
        """
        Delete draft of a published dataset.
        """
        cr = self._create_dataset(with_files=False)
        draft_cr = self._create_draft(cr['id'])

        response = self.client.delete('/rest/v2/datasets/%d' % draft_cr['id'], format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        # draft should be deleted permanently
        draft_found = CR.objects_unfiltered.filter(pk=draft_cr['id']).exists()
        self.assertEqual(draft_found, False)

        # ensure original now has a link to next_draft
        response = self.client.get('/rest/v2/datasets/%s' % cr['id'], format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('next_draft' in response.data, False, 'next_draft link should be gone')
