import logging
from django.conf import settings

from .serializers import StatementDeserializer, SourcesDeserializer
from .consumer import Consumer

logger = logging.getLogger('pp.demagog_consumer')


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
        return [statement['attributes']['sources'] for statement in deserializer.validated_data]

    def get_sources_list(self):
        response = self.get('/sources_list', params={
            'client': 'pp'
        })
        deserializer = SourcesDeserializer(data=response.get('data'))
        if not deserializer.is_valid():
            raise DemagogConsumer.ConsumingDataError(self.request_error(deserializer.errors))
        return deserializer.validated_data['attributes']['sources']


def consume_all_statements():

    consumer = DemagogConsumer()

    current_page = 1
    total_pages = None

    while current_page <= total_pages:
        logger.info('Consuming page {} of {}'.format(current_page, total_pages if current_page > 1 else 'unknown'))
        try:
            json_data = consumer.get_all_statements()
        except Consumer.ConsumingResponseError as e:
            logger.error(e.message)
        else:
            total_pages = json_data.get('total_pages', 1)

            # Load data here

        current_page += 1



def consume_sources_list():


    return sources_list