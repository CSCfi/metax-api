from datetime import datetime, timedelta
from decimal import Decimal
from jsonschema import validate as json_validate
from uuid import UUID

from django.core.management import call_command
from django.test import TestCase

from metax_api.tests.utils import get_json_schema, datetime_format, test_data_file_path, TestClassUtils
from metax_api.models import File

d = print

class FileModelBasicTest(TestCase, TestClassUtils):

    """
    Verify that at least test data is correct on a basic level, and the model contains
    the expected fields.
    """

    file_field_names = (
        'download_url',
        'replication_path',
        'identifier',
        'byte_size',
        'checksum_value',
        'file_name',
        'file_format',
        'file_modified',
        'file_path',
        'checksum_checked',
        'checksum_algorithm',
        'access_group',
        'open_access',
        'file_characteristics',
        'file_storage_id',
        'xmlmetadata',
    )

    common_fields_names = (
        'id',
        'active',
        'removed',
        'modified_by_api',
        'modified_by_user_id',
        'created_by_api',
        'created_by_user_id',
    )

    @classmethod
    def setUpClass(cls):
        """
        Loaded only once for test cases inside this class.
        """
        call_command('loaddata', test_data_file_path)
        super(FileModelBasicTest, cls).setUpClass()

    def setUp(self):
        file_from_test_data = self._get_object_from_test_data('file')
        self.identifier = file_from_test_data['identifier']
        self.result_file_name = file_from_test_data['file_name']

    def test_get_by_identifier(self):
        file = File.objects.get(identifier=self.identifier)
        self.assertEqual(file.file_name, self.result_file_name)

    def test_validate_file_characteristics_json(self):
        file = File.objects.get(identifier=self.identifier)

        try:
            json_validate(file.file_characteristics, get_json_schema('file'))
            json_validation_success = True
        except Exception as e:
            d(e)
            json_validation_success = False

        self.assertEqual(json_validation_success, True, 'file.file_characteristics failed json schema validation')

    def test_model_fields_as_expected(self):
        actual_model_fields = [ f.name for f in File._meta.get_fields() ]
        self._test_model_fields_as_expected(self.file_field_names + self.common_fields_names, actual_model_fields)

    def test_model_field_values(self):
        test_file_data = {
            "download_url": "http://some.url.csc.fi/1",
            "replication_path": "empty",
            "identifier": self.identifier,
            "byte_size": 0,
            "removed": False,
            "checksum_value": "habeebit",
            "modified_by_api": "2017-05-23T10:07:22.559656Z",
            "file_name": "file_name_1",
            "file_format": "html/text",
            "file_modified": "2017-05-23T14:41:59.507392Z",
            "file_path": "/some/path/",
            "checksum_checked": None,
            "checksum_algorithm": "sha2",
            "access_group": "my group",
            "open_access": False,
            "created_by_api": "2017-05-23T10:07:22.559656Z",
        }
        test_file_characteristics = {
            "application_name": "Application Name",
            "description": "A nice description 10",
            "metadata_modified": "2014-01-17T08:19:31Z",
            "file_created": "2014-01-17T08:19:31Z",
            "encoding": "utf-8",
            "title": "A title 10"
        }

        file = File.objects.get(identifier=self.identifier)

        self._dict_comparison(test_file_data, file)
        self._dict_comparison(test_file_characteristics, file.file_characteristics)

    def _dict_comparison(self, test_data, object):
        """
        Run through all keys in test data/object and see that all expected fields are present
        and their values are as expected.
        """
        for field in test_data.keys():

            if isinstance(object, dict):
                # dict, or "json field"
                value = object[field]
            else:
                # django model
                value = getattr(object, field)

            try:
                if isinstance(value, UUID):
                    self.assertEqual(test_data[field], str(value))
                elif isinstance(value, Decimal):
                    self.assertEqual(Decimal(test_data[field]), Decimal(value))
                elif isinstance(value, datetime):
                    # timezones, man
                    self.assertEqual(datetime.strptime(test_data[field], datetime_format) + timedelta(hours=3), value)
                else:
                    self.assertEqual(test_data[field], value)
            except Exception as e:
                d(type(value))
                d(test_data[field])
                d(value)
                raise
