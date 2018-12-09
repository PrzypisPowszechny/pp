from functools import partial

import requests


class Consumer:
    api_name = None
    base_url = None
    content_type = 'text/plain'

    def __init__(self, api_name=None, base_url=None, content_type=None):
        self.api_name = api_name or self.api_name
        self.base_url = base_url or self.base_url
        self.content_type = content_type or self.content_type

    class ConsumingError(BaseException):
        pass

    class ConsumingResponseError(ConsumingError):
        pass

    class ConsumingDataError(ConsumingError):
        pass

    def _make_request(self, method, endpoint_path, params=None, data=None):
        url = '%s%s' % (self.base_url, endpoint_path)

        if method == 'get':
            method_func = requests.get
        elif method == 'post':
            method_func = requests.post
        else:
            raise ValueError('Non supported method')
        try:
            response = method_func(
                url=url,
                params=params,
                data=data,
                headers={"Content-Type": self.content_type},
                timeout=10.0,
            )
        except requests.exceptions.RequestException as error:
            raise self.ConsumingResponseError(self.request_error(getattr(error, 'message', error)))

        if not (200 <= response.status_code < 300):
            raise self.ConsumingResponseError(self.request_status_error(url, response.status_code, response.content))

        return response

    def get(self, endpoint_path, params=None):
        return self._make_request('get', endpoint_path, params=params)

    def post(self, endpoint_path, data=None):
        return self._make_request('post', endpoint_path, data=data)

    def request_error(self, reason):
        return '{} request error: {}'.format(self.api_name, reason)

    def request_deserialize_error(self, reason, for_endpoint=None, for_params=None):
        for_endpoint_text = 'to endpoint {} '.format(for_endpoint) if for_endpoint is not None else ''
        for_params_text = 'with params {} '.format(for_params) if for_params is not None else ''
        return '{api_name} request {for_endpoint_text}{for_params_text}deserialization error: {reason}'.format(
            api_name=self.api_name, for_endpoint_text=for_endpoint_text, for_params_text=for_params_text, reason=reason
        )

    def request_status_error(self, url, status_code, response_content):
        return '{api_name} request to {url} unexpected status {status}. Response: \n {content}'.format(
            api_name=self.api_name, url=url, status=status_code, content=response_content
        )


class JSONConsumer(Consumer):
    content_type = 'application/json'

    def get(self, endpoint_path, params=None):

        response = super().get(endpoint_path, params)

        try:
            json_data = response.json()
        except (TypeError, KeyError, ValueError):
            raise self.ConsumingResponseError('{} response is malformed and cannot be loaded as json'
                                              .format(self.api_name))

        return json_data
