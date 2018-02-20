import datetime

from django.utils import timezone
from django.conf import settings
from oaipmh import common
from oaipmh.common import ResumptionOAIPMH
from oaipmh.error import IdDoesNotExistError
from oaipmh.error import NoSetHierarchyError

from metax_api.models.catalog_record import CatalogRecord
from metax_api.services import CatalogRecordService as CRS


class MetaxOAIServer(ResumptionOAIPMH):

    def _get_set_filter(self, set=None):
        # These are the ids of catalogues that use the att catalog
        return [1, 2]

    def _get_filtered_records(self, set, cursor, batch_size, from_=None, until=None):
        if set: # no support for user defined sets yet
            raise NoSetHierarchyError("The repository does not support sets.")

        query_set = None
        if from_ and until:
            query_set = CatalogRecord.objects.filter(date_modified__gte=from_, date_modified__lte=until)
        elif from_:
            query_set = CatalogRecord.objects.filter(date_modified__gte=from_)
        elif until:
            query_set = CatalogRecord.objects.filter(date_modified__lte=until)
        else:
            query_set = CatalogRecord.objects.all()

        if set:
            query_set.filter(data_catalog_id__in=set)
        return query_set[cursor:batch_size]

    def get_oai_dc_urnresolver_metadata(self, record):
        meta = {
            'identifier':  [settings.OAI['ETSIN_URL_TEMPLATE'] % record.urn_identifier, record.urn_identifier]
        }
        return meta

    def get_oai_dc_metadata(self, record):
        meta = {
            'identifier':  [settings.OAI['ETSIN_URL_TEMPLATE'] % record.urn_identifier, record.urn_identifier]
        }
        return meta

    def get_oai_datacite_metadata(self, record):
        datacite_xml = CRS.transform_datasets_to_format(
            {'research_dataset': record.research_dataset},'datacite', False
            )
        meta = {
            'datacentreSymbol': 'Metax',
            'schemaVersion': '4.1',
            'payload': datacite_xml
        }
        return meta

    def _get_metadata_for_record(self, record, metadata_prefix):
        meta = {}
        if metadata_prefix == 'oai_dc':
            meta = self.get_oai_dc_metadata(record)
        elif metadata_prefix == 'oai_datacite':
            meta = self.get_oai_datacite_metadata(record)
        elif metadata_prefix == 'oai_dc_urnresolver':
            meta = self.get_oai_dc_urnresolver_metadata(record)

        metadata = {}
        # Fixes the bug on having a large dataset being scrambled to individual
        # letters
        for key, value in meta.items():
            if not isinstance(value, list):
                metadata[str(key)] = [value]
            else:
                metadata[str(key)] = value
        return metadata

    def _get_header_timestamp(self, record):
        timestamp = None
        if record.date_modified:
            timestamp = record.date_modified
        else:
            timestamp = record.date_created
        return timezone.make_naive(timestamp)

    def identify(self):
        first = CatalogRecord.objects.filter(
            data_catalog_id__in=self._get_set_filter()).order_by(
                'date_created').values_list('date_created', flat=True).first()
        if first:
            first = timezone.make_naive(first)
        else:
            first = datetime.datetime.now()

        return common.Identify(
            repositoryName=settings.OAI['REPOSITORY_NAME'],
            baseURL=settings.OAI['BASE_URL'],
            protocolVersion="2.0",
            adminEmails=[settings.OAI['ADMIN_EMAIL']],
            earliestDatestamp=first,
            deletedRecord='no',
            granularity='YYYY-MM-DDThh:mm:ssZ',
            compression=['identity'])

    def listMetadataFormats(self, identifier=None):
        '''List available metadata formats.
        '''
        return [('oai_dc',
                'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                'http://www.openarchives.org/OAI/2.0/oai_dc/'),
                ('oai_datacite',
                'https://schema.datacite.org/meta/kernel-4.1/metadata.xsd',
                'https://schema.datacite.org/meta/kernel-4.1/'),
                ('oai_dc_urnresolver',
                'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                'http://www.openarchives.org/OAI/2.0/oai_dc/')
                ]

    def listSets(self, cursor=None, batch_size=None):
        data = []
        return data

    def listIdentifiers(self, metadataPrefix=None, set=None, cursor=None,
                        from_=None, until=None, batch_size=None):
        records = self._get_filtered_records(set, cursor, batch_size, from_, until)
        data = []
        for record in records:
            data.append(common.Header('', record.urn_identifier, self._get_header_timestamp(record), ['metax'], False))
        return data

    def listRecords(self, metadataPrefix=None, set=None, cursor=None, from_=None,
                    until=None, batch_size=None):
        data = []
        records = self._get_filtered_records(set, cursor, batch_size, from_, until)
        for record in records:
            metadata = self._get_metadata_for_record(record, metadataPrefix)
            item = (common.Header('', record.urn_identifier, self._get_header_timestamp(record), ['metax'], False),
                common.Metadata('', metadata), None)
            data.append(item)
        return data

    def getRecord(self, metadataPrefix, identifier):
        try:
            record = CatalogRecord.objects.get(data_catalog_id__in=self._get_set_filter(),
                research_dataset__contains={'urn_identifier': identifier })
        except:
            # This now includes both MultipleObjectsReturned (should not happen, because urn
            # should be unique) and DoesNotExist
            raise IdDoesNotExistError("No dataset with id %s" % identifier)
        metadata = self._get_metadata_for_record(record, metadataPrefix)

        return (common.Header('', record.urn_identifier, self._get_header_timestamp(record), ['metax'], False),
            common.Metadata('', metadata), None)
