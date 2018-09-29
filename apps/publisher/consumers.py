import requests
from django.conf import settings

from .serializers import StatementDeserializer, SourcesDeserializer


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

    def _make_request(self, method, endpoint_path, params=None):
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
                headers={"Content-Type": self.content_type},
                timeout=10.0,
            )
        except requests.exceptions.RequestException as error:
            raise self.ConsumingResponseError(self.request_error(getattr(error, 'message', error)))

        if not (200 <= response.status_code < 300):
            raise self.ConsumingResponseError('{} request to {} unexpected status {}. Response: \n {}'.format(
                self.api_name, url, response.status_code, response.content)
            )

        return response

    def get(self, endpoint_path, params=None):
        return self._make_request('get', endpoint_path, params)

    def post(self, endpoint_path, params=None):
        return self._make_request('get', endpoint_path, params)

    def request_error(self, reason):
        return '{} request error: {}'.format(self.api_name, reason)


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


# TODO: Establish convention: some request params omitted as they make no sense in our case,also 'client' val improvised
class DemagogConsumer(Consumer):
    api_name = 'Demagog API'
    base_url = settings.DEMAGOG_API_URL

    def get_all_statements(self, page=1):
        response = self.get('/', params={
            'page': page,
            'q': 'all',
            'client': 'pp'
        })
        if 'total_pages' not in response or 'current_page' not in response:
            raise DemagogConsumer.ConsumingDataError(self.request_error('no total_pages/current_page'))
        deserializer = StatementDeserializer(many=True, data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_error(deserializer.errors))
        return response['total_pages'], response['current_page'], deserializer.validated_data

    def get_statements(self, source_url):
        response = self.get('/statements', params={
            'uri': source_url,
            'client': 'pp'
        })
        deserializer = StatementDeserializer(many=True, data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_error(deserializer.errors))
        return deserializer.validated_data

    def get_sources_list(self):
        response = self.get('/sources_list', params={
            'client': 'pp'
        })
        deserializer = SourcesDeserializer(data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_error(deserializer.errors))
        return deserializer.validated_data['attributes']['sources']
