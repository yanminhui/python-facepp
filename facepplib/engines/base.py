"""
Base engine that defines common behaviour and settings for all engines.
"""

import copy
import mimetypes
import os

from .. import exceptions


class BaseEngine(object):
    chunk = 100  # Default limit is 100.

    def __init__(self, api_key, api_secret, **options):
        """
        :param string api_key: (required). Your registered API Key to call API.
        :param string api_secret: (required). Your registered API Secret to call API.
        :param dict requests: (optional). Connection options.
        :param bool return_raw_response (optional). Whether to return raw or json encoded responses.
        """
        self.api_key = api_key
        self.api_secret = api_secret

        self.return_raw_response = options.pop('return_raw_response', False)

        self.requests = dict(dict(headers={}, params={}, data={}), **options.get('requests', {}))
        self.session = self.create_session(**self.requests)

    @staticmethod
    def create_session(**params):
        """
        Creates a session object that will be used to make requests to FacePP.

        :param dict params: (optional). Session params.
        """
        raise NotImplementedError

    @staticmethod
    def construct_request_kwargs(method, headers, params, data):
        """
        Constructs kwargs that will be used in all requests to FacePP.

        :param string method: (required). HTTP verb to use for the request.
        :param dict headers: (required). HTTP headers to send with the request.
        :param dict params: (required). Params to send in the query string.
        :param data: (required). Data to send in the body of the request.
        :type data: dict, bytes or file-like object
        """
        kwargs = {'files': {}, 'data': data or {}, 'params': params or {}, 'headers': headers or {}}

        # Image_file need file-like object.
        if method in ('post', 'put', 'patch'):
            changes = []
            for img in kwargs['data']:
                if not img.startswith('image_file'):
                    continue
                image_file = kwargs['data'][img]
                fn = os.path.basename(image_file)
                fp = open(image_file, 'rb')
                ft = mimetypes.guess_type(image_file)[0] or 'application/octet-stream'
                kwargs['files'].setdefault(img, (fn, fp, ft))
                changes.append(img)
            for img in changes:
                kwargs['data'].pop(img)
        return kwargs

    @staticmethod
    def destroy_request_kwargs(method, **kwargs):
        """
        Destroy kwargs that had been used in all requests to FaceePP.

        :param method: (required). HTTP verb to use for the request.
        :param kwargs: (required). Being used in all requests to FaceePP.
        """
        # Close image_file.
        if method in ('post', 'put', 'patch') and 'files' in kwargs:
            files = kwargs['files']
            if not isinstance(files, dict):
                return None
            for field, image_file in files.items():
                if not isinstance(image_file, tuple) or len(image_file) < 2:
                    continue
                fp = image_file[1]
                if not hasattr(fp, 'closed') or fp.closed:
                    continue
                fp.close()

    def request(self, method, url, headers=None, params=None, data=None):
        """
        Makes a single request to FacePP and returns processed response.

        :param string method: (required). HTTP verb to use for the request.
        :param string url: (required). URL of the request.
        :param dict headers: (optional). HTTP headers to send with the request.
        :param dict params: (optional). Params to send in the query string.
        :param data: (optional). Data to send in the body of the request.
        :type data: dict, bytes or file-like object
        """
        # Data append api_key and api_secret.
        data_cp = copy.deepcopy(data) if data else None
        if isinstance(data_cp, dict):
            data_cp.setdefault('api_key', self.api_key)
            data_cp.setdefault('api_secret', self.api_secret)

        kwargs = self.construct_request_kwargs(method, headers, params, data_cp)
        response = self.session.request(method, url, **kwargs)
        self.destroy_request_kwargs(method, **kwargs)
        return self.process_response(response)

    def bulk_request(self, method, url, container, **data):
        """
        Makes needed preparations before launching the active engine's request process.

        :param string method: (required). HTTP verb to use for the request.
        :param string url: (required). URL of the request.
        :param string container: (required).
        :param dict data (optional). data that should be used for resource retrieval.
        """
        limit = data.pop('limit') or self.chunk
        start = data.get('start') or 1
        next_start = None

        response = self.request(method, url, data=dict(data, start=start))

        # Resource supports start/next on FacePP level
        if all(response.get(param) is not None for param in ('next', )):
            next_start = response['next']
            results = response

            container_size = next_start - start
            while limit > container_size:
                start = next_start
                response = self.request(method, url, data=dict(data, start=start))

                next_start = response.get('next')
                results[container].extend(response[container])
                results['next'] = next_start

                if next_start:
                    container_size += (next_start - start)
                else:
                    break

        # We have to mimic start/next if a resource
        # doesn't support this feature on FacePP level
        else:
            results = response[container]

        return results if isinstance(results, (list, tuple)) else [results], next_start

    def process_response(self, response):
        """
        Processes response received from FacePP.

        :param obj response: (required). Response object with response details.
        :return raw_response, True (if response is null) or json
        """
        if response.history:
            r = response.history[0]
            if r.is_redirect and r.request.url.startswith('http://') and response.request.url.startswith('https://'):
                raise exceptions.HTTPProtocolError

        status_code = response.status_code

        if status_code in (200, 201, 204):
            if self.return_raw_response:
                return response
            elif not response.content.strip():
                return True
            else:
                try:
                    return response.json()
                except (ValueError, TypeError):
                    raise exceptions.JSONDecodeError(response)

        error_reason = None
        error_details = None
        try:
            response_failed = response.json()
            error_message = response_failed['error_message']
            if not isinstance(error_message, str) and not isinstance(error_message, unicode):
                error_message = ''
            split_char = ':'
            split_fields = error_message.split(split_char)
            error_reason = split_char.join(split_fields[:1]).strip()
            error_details = split_char.join(split_fields[1:]).strip()
        except (ValueError, TypeError):
            raise exceptions.JSONDecodeError(response)

        if not error_reason:
            error_reason = ''
        if not error_details:
            error_details = ''

        for k_status_code, v_tuple in exceptions.exception_table.items():
            if k_status_code != status_code:
                continue
            for arg_num, s2e in enumerate(v_tuple):
                for s, e in s2e.items():
                    if s != error_reason:
                        continue
                    raise e if arg_num == 0 else e(error_details)

        raise exceptions.UnknownError(status_code)

