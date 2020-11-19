# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

import logging

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from metax_api.exceptions import Http403
from metax_api.models import Directory
from metax_api.services import FileService
from .common_rpc import CommonRPC

_logger = logging.getLogger(__name__)


class DirectoryRPC(CommonRPC):

    @action(detail=False, methods=['get'], url_path="update_byte_sizes_and_file_counts")
    def update_byte_sizes_and_file_counts(self, request):
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

        return Response(status=status.HTTP_204_NO_CONTENT)