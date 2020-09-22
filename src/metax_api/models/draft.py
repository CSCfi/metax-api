
from .catalog_record_v2 import CatalogRecordV2
from django.db import models
import logging
_logger = logging.getLogger(__name__)
from metax_api.utils import (
    datetime_to_str,
    DelayedLog,
    generate_doi_identifier,
    generate_uuid_identifier,
    get_identifier_type,
    get_tz_aware_now_without_micros,
    IdentifierType,
)
class Draft(CatalogRecordV2):

    is_merged = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    @classmethod
    def create(cls, original_record:CatalogRecordV2):

        # set child values from parent
        obj = cls()
        for field in original_record._meta.fields:
            setattr(obj, field.attname, getattr(original_record, field.attname))
        Draft.objects.filter(id=obj.id).update(next_dataset_version=None, previous_dataset_version=None, dataset_version_set=None, preservation_identifier=None)
        obj.next_dataset_version = None
        obj.identifier = generate_uuid_identifier()
        obj.research_dataset['metadata_version_identifier'] = generate_uuid_identifier()
        obj.api_meta['version'] = obj.api_version
        obj.state = cls.STATE_DRAFT
        if original_record.files.exists():
            # note: _directory_data field is already copied when the template is made
            obj.files.add(*original_record.files.all())
        return obj

    def save(self, original_record:CatalogRecordV2, *args, **kwargs):
        """
        Create a new draft of a published dataset, that can later be merged back to the original published dataset.
        """
        _logger.info('Creating a draft of a published dataset...')

        # v2 api successfully invoked, change the api version to prevent further updates on v1 api
        self._set_api_version()
        super(Draft, self).save(*args, **kwargs)

        log_args = {
            'event': 'dataset_draft_created',
            'user_id': self.user_created or self.service_created,
            'catalogrecord': {
                'identifier': self.identifier,
                'preferred_identifier': self.preferred_identifier,
                'data_catalog': self.data_catalog.catalog_json['identifier'],
                'date_created': datetime_to_str(self.created),
                'metadata_owner_org': self.metadata_owner_org,
                'state': self.state,
            }
        }

        self.add_post_request_callable(DelayedLog(**log_args))



