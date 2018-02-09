from json import dumps as json_dumps
import logging

from django.http import StreamingHttpResponse

_logger = logging.getLogger(__name__)


class StreamHttpResponse(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Then comes the response
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        # import ipdb; ipdb.set_trace()

        if request.method == 'GET' and isinstance(response.data, list) and self._check_query_param(request, 'stream'):
            resp = StreamingHttpResponse(self._stream_response(response))
            resp._headers['content-type'] = ('Content-Type', 'application/json; charset=utf=8')
            return resp

        return response

    def _check_query_param(self, request, param):
        """
        request is a gunicorn WSGI request, not a django request which has the query params all figured out
        already. Seek the value of a boolean query param from a string blob which represents the query parameters.
        """
        qs = request.META.get('QUERY_STRING', None)

        if not qs:
            return False
        elif 'stream' not in qs:
            return False

        # QUERY_STRING may look like "stuff=true&more_stuff=false&even_more_stuff_but_no_value"

        params = qs.split('&')

        for p in params:
            if not p.startswith(param):
                continue
            split = p.split('=')
            if len(split) == 1:
                # only name was specified, which counts as a True
                return True
            else:
                if split[1] in ('true', 'false'):
                    return split[1] == 'true'
                return False
        return False

    def _stream_response(self, response):
        for item in response.data:
            if isinstance(item, dict):
                yield json_dumps(item)
            else:
                yield item
