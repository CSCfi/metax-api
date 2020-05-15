# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

from collections import defaultdict

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from metax_api.api.rest.base.serializers import DirectorySerializer
from metax_api.services.pagination import DirectoryPagination
from rest_framework.pagination import LimitOffsetPagination
from metax_api.exceptions import Http400, Http403, Http501
from metax_api.models import Directory
from metax_api.services import CommonService, FileService
from .common_view import CommonViewSet


class DirectoryViewSet(CommonViewSet):

    serializer_class = DirectorySerializer
    pagination_class = DirectoryPagination
    object = Directory
    select_related = ['parent_directory']
    lookup_field_other = 'identifier'

    def get_api_name(self):
        """
        Overrided due to not being able to follow common plural pattern...
        """
        return 'directories'

    def list(self, request, *args, **kwargs):
        raise Http501()

    def update(self, request, *args, **kwargs):
        raise Http501()

    def update_bulk(self, request, *args, **kwargs):
        raise Http501()

    def partial_update(self, request, *args, **kwargs):
        raise Http501()

    def partial_update_bulk(self, request, *args, **kwargs):
        raise Http501()

    def create(self, request, *args, **kwargs):
        raise Http501()

    def destroy(self, request, *args, **kwargs):
        raise Http501()

    def _get_directory_contents(self, request, identifier=None):
        """
        A wrapper to call FS to collect and validate parameters from the request,
        and then call FS.get_directory_contents().
        """
        paginate = CommonService.get_boolean_query_param(request, 'pagination')
        include_parent = CommonService.get_boolean_query_param(request, 'include_parent')
        dirs_only = CommonService.get_boolean_query_param(request, 'directories_only')
        recursive = CommonService.get_boolean_query_param(request, 'recursive')
        max_depth = request.query_params.get('depth', 1)
        project_identifier = request.query_params.get('project', None)
        cr_identifier = request.query_params.get('cr_identifier', None)
        not_cr_identifier = request.query_params.get('not_cr_identifier', None)

        # max_depth can be an integer > 0, or * for everything.
        try:
            max_depth = int(max_depth)
        except ValueError:
            if max_depth != '*':
                raise Http400({ 'detail': ['value of depth must be an integer higher than 0, or *'] })
        else:
            if max_depth <= 0:
                raise Http400({ 'detail': ['value of depth must be higher than 0'] })

        if cr_identifier and not_cr_identifier:
            raise Http400({ 'detail':
                ["there can only be one query parameter of 'cr_identifier' and 'not_cr_identifier'"] })

        files_and_dirs = FileService.get_directory_contents(
            identifier=identifier,
            path=request.query_params.get('path', None),
            project_identifier=project_identifier,
            recursive=recursive,
            max_depth=max_depth,
            dirs_only=dirs_only,
            include_parent=include_parent,
            cr_identifier=cr_identifier,
            not_cr_identifier=not_cr_identifier,
            request=request
        )

        if isinstance(files_and_dirs, dict):
            if files_and_dirs.get('directories') and files_and_dirs['directories'][0].get('directory_path'):
                files_and_dirs['directories'] = sorted(files_and_dirs['directories'],
                    key=lambda k: k['directory_path'].lower())

            if files_and_dirs.get('files') and files_and_dirs['files'][0].get('file_path'):
                files_and_dirs['files'] = sorted(files_and_dirs['files'], key=lambda k: k['file_path'].lower())

        elif files_and_dirs and files_and_dirs[0].get('file_path'):
            files_and_dirs = sorted(files_and_dirs, key=lambda k: k['file_path'].lower())

        if paginate:
            if isinstance(files_and_dirs, dict):
                paginated = self.paginate_queryset(files_and_dirs)
                if include_parent:
                    for k, v in files_and_dirs.items():
                        if k not in ['directories', 'files']:
                            paginated[k] = v
                return self.get_paginated_response(paginated)
            else:
                paginator = LimitOffsetPagination()
                context = paginator.paginate_queryset(files_and_dirs, request)
                return paginator.get_paginated_response(context)

        return Response(files_and_dirs)

    @detail_route(methods=['get'], url_path="files")
    def get_files(self, request, pk=None):
        """
        Return a list of child files and directories of a directory.
        """
        return self._get_directory_contents(request, identifier=pk)

    @list_route(methods=['get'], url_path="files")
    def get_files_by_path(self, request):
        """
        Return a list of child files and directories of a directory, queried
        by path and project identifier, instead of directly by identifier
        """
        errors = defaultdict(list)

        if 'project' not in request.query_params:
            errors['detail'].append('project is a required query parameter')
        if 'path' not in request.query_params:
            errors['detail'].append('path is a required query parameter')

        if errors:
            raise Http400(errors)

        return self._get_directory_contents(request)

    @list_route(methods=['get'], url_path="root")
    def get_project_root_directory(self, request):
        """
        Return root directory for a project. This is useful when starting
        to browse files for a project, when individual root-level directory identifier
        is not yet known.

        Example: GET /directories/root?project=projext_x
        """
        if 'project' not in request.query_params:
            raise Http400('project is a required query parameter')

        if not request.user.is_service:
            FileService.check_user_belongs_to_project(request, request.query_params['project'])

        root_dirs = FileService.get_project_root_directory(request.query_params['project'])

        return Response(root_dirs)

    @list_route(methods=['get'], url_path="update_byte_sizes_and_file_counts")
    def update_byte_sizes_and_file_counts(self, request): # pragma: no cover
        """
        Calculate byte sizes and file counts for all dirs in all projects. Intended to be called after
        importing test data.

        If needed there should be no harm in calling this method again at any time in an attempt to
        correct mistakes in real data.
        """
        if request.user.username != 'metax':
            raise Http403

        for p in Directory.objects.all().distinct('project_identifier').values_list('project_identifier', flat=True):
            FileService.calculate_project_directory_byte_sizes_and_file_counts(p)

        return Response()
