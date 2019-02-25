import logging

from django.conf import settings

from apps.consumers import JSONConsumer
from .serializers import StatementDeserializer, SourcesDeserializer, split_valid_urls

logger = logging.getLogger('pp.publisher')


# TODO: Establish convention: some request params omitted as they make no sense in our case,also 'client' val improvised
class DemagogConsumer(JSONConsumer):
    api_name = 'Demagog API'
    base_url = settings.DEMAGOG_API_URL

    def get(self, endpoint_path, params=None):
        logger.debug('Querying {api_name} endpoint {endpoint} with params: {params}'.format(
            api_name=self.api_name, endpoint=endpoint_path, params=params
        ))
        return super().get(endpoint_path, params)

    def get_all_statements(self, page=1):
        endpoint = '/statements'
        response = self.get(endpoint, params={
            'page': page,
            'q': 'all',
            'client': 'pp'
        })
        if 'total_pages' not in response or 'current_page' not in response:
            raise DemagogConsumer.ConsumingDataError(
                self.request_error('response does not contain total_pages or current_page field')
            )
        deserializer = StatementDeserializer(many=True, data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_deserialize_error(
                deserializer.errors, for_endpoint=endpoint,
            ))
        return response['total_pages'], response['current_page'], deserializer.validated_data

    # TODO: reshape into fully object-oriented programming model, with method acting as separate class
    def get_statements(self, source_url):
        endpoint = '/statements'
        response = self.get(endpoint, params={
            'uri': source_url,
            'client': 'pp'
        })
        deserializer = StatementDeserializer(many=True, data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_deserialize_error(
                deserializer.errors, for_endpoint=endpoint, for_params={'uri': source_url})
            )
        return deserializer.validated_data

    def get_sources_list(self):
        endpoint = '/sources_list'
        response = self.get(endpoint, params={
            'client': 'pp'
        })
        deserializer = SourcesDeserializer(data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_deserialize_error(
                deserializer.errors, for_endpoint=endpoint,
            ))

        valid_sources, invalid_sources = split_valid_urls(deserializer.validated_data['attributes']['sources'])
        if invalid_sources:
            logging.warning(self.request_deserialize_error(
                '{invalid}/{all} of loaded sources are not valid urls: \n {sources}'.format(
                    invalid=len(invalid_sources), all=len(invalid_sources) + len(valid_sources), sources=invalid_sources
                ), for_endpoint=endpoint
            ))
        return valid_sources
