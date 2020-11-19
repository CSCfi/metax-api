# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

import logging

from rest_framework.decorators import action
from rest_framework.response import Response

from metax_api.services import ApiErrorService
from .common_rpc import CommonRPC

_logger = logging.getLogger(__name__)


class ApiErrorRPC(CommonRPC):
    @action(detail=False, methods=['post'], url_path="flush_errors")
    def flush_errors(self, request):
        _logger.info('%s called by %s' % (request.META['PATH_INFO'], request.user.username))
        files_deleted_count = ApiErrorService.flush_errors()
        return Response(data={ 'files_deleted': files_deleted_count }, status=200)