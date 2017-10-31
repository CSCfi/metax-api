from django.http import Http404
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from metax_api.exceptions import Http400
from metax_api.models import File, XmlMetadata
from metax_api.renderers import XMLRenderer
from metax_api.services import CommonService
from .common_view import CommonViewSet
from ..serializers import FileSerializer, XmlMetadataSerializer

import logging
_logger = logging.getLogger(__name__)
d = logging.getLogger(__name__).debug


class FileViewSet(CommonViewSet):

    authentication_classes = ()
    permission_classes = ()

    # note: override get_queryset() to get more control
    queryset = File.objects.all()
    serializer_class = FileSerializer
    object = File

    lookup_field = 'pk'

    # allow search by external identifier (urn, or whatever string in practice) as well
    lookup_field_other = 'identifier'

    def __init__(self, *args, **kwargs):
        self.set_json_schema(__file__)
        super(FileViewSet, self).__init__(*args, **kwargs)

    def get_object(self):
        """
        future todo:
        - query params:
            - owner_email (string)
            - fields (list of strings)
            - offset (integer) (paging)
            - limit (integer) (limit for paging)
        """
        return super(FileViewSet, self).get_object()

    @detail_route(methods=['get', 'post', 'put', 'delete'], url_path='xml')
    def xml_handler(self, request, pk=None):
        file = self.get_object()

        if request.method == 'GET':
            return self._get_xml(request, file)
        else:
            if 'namespace' not in request.query_params:
                raise Http400('namespace is a required query parameter')

            if request.method == 'PUT':
                return self._update_xml(request, file)
            elif request.method == 'POST':
                return self._create_xml(request, file)
            elif request.method == 'DELETE':
                return self._delete_xml(request, file)
            else:
                raise Http404

    def _get_xml(self, request, file):
        if 'namespace' in request.query_params:
            # get single requested xml metadata by namespace
            try:
                xml_metadata = file.xmlmetadata_set.get(namespace=request.query_params['namespace'])
            except XmlMetadata.DoesNotExist:
                raise Http404
            request.accepted_renderer = XMLRenderer()
            return Response(data=xml_metadata.xml, status=status.HTTP_200_OK)

        else:
            # return list of namespaces of xml metadatas associated with the file
            xml_namespaces = file.xmlmetadata_set.all().values_list('namespace', flat=True)
            request.accepted_renderer = JSONRenderer()
            return Response(data=[ ns for ns in xml_namespaces ], status=status.HTTP_200_OK)

    def _create_xml(self, request, file):
        try:
            file.xmlmetadata_set.get(namespace=request.query_params['namespace'])
        except XmlMetadata.DoesNotExist:
            # good - create for the first time
            pass
        else:
            raise Http400('xml metadata with namespace %s already exists' % request.query_params['namespace'])

        new_xml_metadata = self._xml_request_to_dict_data(request, file)
        serializer = XmlMetadataSerializer(data=new_xml_metadata)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        request.accepted_renderer = XMLRenderer()
        return Response(data=serializer.instance.xml, status=status.HTTP_201_CREATED)

    def _update_xml(self, request, file):
        try:
            xml_metadata = file.xmlmetadata_set.get(namespace=request.query_params['namespace'])
        except XmlMetadata.DoesNotExist:
            raise Http404

        new_xml_metadata = self._xml_request_to_dict_data(request, file)
        serializer = XmlMetadataSerializer(xml_metadata, data=new_xml_metadata)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    def _delete_xml(self, request, file):
        try:
            xml_metadata = file.xmlmetadata_set.get(namespace=request.query_params['namespace'])
        except XmlMetadata.DoesNotExist:
            raise Http404
        xml_metadata.delete()
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    def _xml_request_to_dict_data(self, request, file):
        """
        Take the original request, and its associated file, and return them in a form
        that is digestable by the XmlMetadataSerializer.
        """
        common_info = CommonService.update_common_info(request, return_only=True)
        new_xml_metadata = {
            'file': file.id,
            'xml': request.data,
            'namespace': request.query_params['namespace']
        }
        new_xml_metadata.update(common_info)
        return new_xml_metadata
