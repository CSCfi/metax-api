# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from metax_api.models import CatalogRecord, Directory, File
from metax_api.tests.utils import TestClassUtils, test_data_file_path


class FileRPCTests(APITestCase, TestClassUtils):

    @classmethod
    def setUpClass(cls):
        """
        Loaded only once for test cases inside this class.
        """
        super().setUpClass()

    def setUp(self):
        super().setUp()
        call_command('loaddata', test_data_file_path, verbosity=0)
        self._use_http_authorization(username='metax')

class DeleteProjectTests(FileRPCTests):

    """
    NoteToSelf: how to test ida/tpas user authentication? Should every ida/tpas user has right to delete any project?
    """

    def test_wrong_parameters(self):
        self._use_http_authorization()
        response = self.client.delete('/rpc/files/delete_project?project_identifier=research_project_112')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #wrong_user
        self._set_http_authorization('testuser')
        response = self.client.delete('/rpc/files/delete_project')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #no_project_identifier
        self._use_http_authorization(username='metax')
        response = self.client.delete('/rpc/files/delete_project')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #nonexisting_project_identifier:
        response = self.client.delete('/rpc/files/delete_project?project_identifier=non_existing')
        self.assertEqual(response.data['deleted_files_count'], 0)

    def test_known_project_identifier(self):
        response = self.client.delete('/rpc/files/delete_project?project_identifier=research_project_112')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_files_are_marked_deleted(self):
        self.client.delete('/rpc/files/delete_project?project_identifier=research_project_112')
        files_count_not_marked_deleted = File.objects\
            .filter(project_identifier='research_project_112', removed=False)\
            .count()
        self.assertEqual(files_count_not_marked_deleted, 0)

    def test_directories_are_marked_deleted(self):
        self.client.delete('/rpc/files/delete_project?project_identifier=research_project_112')
        directories_count_not_marked_deleted = Directory.objects\
            .filter(project_identifier='research_project_112', removed=False)\
            .count()
        self.assertEqual(directories_count_not_marked_deleted, 0)

    def test_datasets_are_marked_deprecated(self):
        self.client.delete('/rpc/files/delete_project?project_identifier=project_x')

        file_ids = [ id for id in File.objects.filter(project_identifier='project_x').values_list('id', flat=True) ]
        datasets_count_not_marked_deprecated = CatalogRecord.objects\
            .filter(files__in=file_ids, deprecated=False)\
            .distinct('id').count()
        self.assertEqual(datasets_count_not_marked_deprecated, 0)
