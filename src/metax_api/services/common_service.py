from datetime import datetime
from json import load as json_load
from os import path
import logging

from rest_framework import status
from rest_framework.serializers import ValidationError

_logger = logging.getLogger(__name__)
d = logging.getLogger(__name__).debug

class CommonService():

    @staticmethod
    def is_primary_key(received_lookup_value):
        if not received_lookup_value:
            return False
        try:
            int(received_lookup_value)
        except ValueError:
            return False
        else:
            return True

    @classmethod
    def create_bulk(cls, request, serializer_class, **kwargs):
        """
        Note: BOTH single and list create

        Create objects to database from a list of dicts or a single dict, and return a list
        of created objects or a single object.

        params:
        request: the http request object
        serializer_class: does the actual saving, knows what kind of object is in question
        """
        common_info = { 'created_by_api': datetime.now() }

        results = None

        if isinstance(request.data, list):

            # dont fail the entire request if only some inserts fail.
            # successfully created rows are added to 'successful', and
            # failed inserts are added to 'failed', with a related error message.
            results = { 'success': [], 'failed': []}

            for row in request.data:

                serializer = serializer_class(data=row, **kwargs)

                try:
                    serializer.is_valid(raise_exception=True)
                except Exception:
                    results['failed'].append({ 'object': serializer.data, 'errors': serializer.errors })
                else:
                    serializer.save(**common_info)
                    results['success'].append({ 'object': serializer.data })

            if results['success']:
                # if even one insert was successful, general status of the request is success
                http_status = status.HTTP_201_CREATED
            else:
                # only if all inserts have failed, return a general failure for the whole request
                http_status = status.HTTP_400_BAD_REQUEST

        else:
            serializer = serializer_class(data=request.data, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save(**common_info)
            http_status = status.HTTP_201_CREATED
            results = serializer.data

        return results, http_status

    @staticmethod
    def get_json_schema(view_file_location, model_name):
        """
        Get the json schema file for model model_name.
        view_file is a __file__ variable
        """
        with open(path.dirname(view_file_location) + '/../schemas/json_schema_%s.json' % model_name, encoding='utf-8') as f:
            return json_load(f)

    @classmethod
    def update_bulk(cls, request, model_obj, serializer_class, **kwargs):
        """
        Note: ONLY list update (PUT and PATCH). Single update uses std rest_framework process.

        Update objects to database from a list of dicts. Bulk update operation requires
        that the payload dict contains a field that can be used to identify the target row
        that is being updated, since a PUT or PATCH to i.e. /datasets or /files will not have
        an identifier in the url.

        If the header If-Unmodified-Since is set, the field modified_by_api from the received
        data row will be compared to same field in the instance being updated, to see if the
        resource has been modified in the meantime. Only the presence of the header is checked
        in bulk update, its value does not matter. For PATCH, the presence of the field
        modified_by_api is an extra requirement in the received data, and an error will be
        returned if it is missing, when the header is set.

        params:
        request: the http request object
        model_obj: the model, used to search the instance being updated
        serializer_class: does the actual saving

        """
        if not isinstance(request.data, list):
            raise ValidationError('request.data is not a list')

        check_modified_since = kwargs['context']['view']._request_has_header('If-Unmodified-Since')
        common_info = { 'modified_by_api': datetime.now() }
        results = { 'success': [], 'failed': []}

        for row in request.data:

            instance = cls._get_object_for_update(model_obj, row, results, check_modified_since)

            if not instance:
                continue

            # note: kwargs will contain kw 'partial', when executed from PATCH
            serializer = serializer_class(instance, data=row, **kwargs)

            try:
                serializer.is_valid(raise_exception=True)
            except Exception:
                results['failed'].append({ 'object': serializer.data, 'errors': serializer.errors })
            else:
                serializer.save(**common_info)
                results['success'].append({ 'object': serializer.data })

        http_status = cls._get_http_status_for_result(results, kwargs.get('partial', False))

        return results, http_status

    @staticmethod
    def update_common_info(request):
        """
        Update fields common for all tables and most actions:
        - last modified timestamp and user
        - created on timestamp and user
        """
        user_id = request.user.id or None

        if not user_id:
            _logger.warning("User id not set; unknown user")

        method = request.stream and request.stream.method or False
        current_time = datetime.now()
        common_info = {}

        if method in ('PUT', 'PATCH', 'DELETE'):
            common_info.update({
                'modified_by_user_id': user_id,
                'modified_by_api': current_time
            })
        elif method == 'POST':
            common_info.update({
                'created_by_user_id': user_id,
                'created_by_api': current_time,
            })
        else:
            pass

        request.data.update(common_info)

    @staticmethod
    def _get_http_status_for_result(results, partial_update):
        if results['success']:
            # if even one operation was successful, general status of the request is success
            if partial_update:
                # PATCH will contain full updated object
                return status.HTTP_200_OK
            else:
                # PUT
                if results['failed']:
                    # some were ok, but since some failed, cant return 204 no_content
                    return status.HTTP_200_OK
                else:
                    # to stay consistent with a single PUT operation, fully successful update
                    # will return no data to the client
                    return status.HTTP_204_NO_CONTENT
        else:
            # only if all rows have failed, return a general failure for the whole request
            return status.HTTP_400_BAD_REQUEST

    @staticmethod
    def _get_object_for_update(model_obj, row, results, check_modified_since):
        """
        Find the target object being updated using a row from the request payload.

        parameters:
        model_obj: the model object used to search the db
        row: the payload from the request
        results: the result-list that will be returned from the api
        check_modified_since: retrieved object should compare its modified_by_api timestamp
            to the corresponding field in the received row. this simulates the use of the
            if-unmodified-since header that is used for single updates.
        """
        instance = None
        try:
            instance = model_obj.objects.get(using_dict=row)
        except model_obj.DoesNotExist:
            results['failed'].append({ 'object': row, 'errors': { 'detail': ['object not found'] }})
        except ValidationError as e:
            results['failed'].append({ 'object': row, 'errors': { 'detail': e.detail } })

        if instance and check_modified_since:
            if 'modified_by_api' not in row:
                results['failed'].append({
                    'object': row,
                    'errors': {
                        'detail': ['Field modified_by_api is required when the header If-Unmodified-Since is set']
                    }
                })
            elif instance.modified_since(row['modified_by_api']):
                results['failed'].append({ 'object': row, 'errors': { 'detail': ['Resource has been modified'] } })
            else:
                # good case - all is good
                pass

        return instance
