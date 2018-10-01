from django.conf import settings

from apps.consumers import JSONConsumer
from .serializers import StatementDeserializer, SourcesDeserializer


# TODO: Establish convention: some request params omitted as they make no sense in our case,also 'client' val improvised
class DemagogConsumer(JSONConsumer):
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