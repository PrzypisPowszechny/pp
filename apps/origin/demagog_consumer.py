import logging

import requests
from django.conf import settings

from .consumer import Consumer

logger = logging.getLogger('pp.demagog_consumer')


class DemagogConsumer(Consumer):

    api_name = 'Demagog API'
    base_url = settings.DEMAGOG_API_URL

    def get_all_statements(self, page=1):
        # TODO: establish convention - some params ignored as they don't make sens in this case, 'client' val improvised
        return self.get('/', params={
            'page': page,
            'q': 'all',
            'client': 'pp'
        })


def consume_all_statements():

    consumer = DemagogConsumer()

    current_page = 1
    total_pages = None

    while current_page <= total_pages:
        logger.info('Consuming page {} of {}'.format(current_page, total_pages if current_page > 1 else 'unknown'))
        try:
            json_data = consumer.get_all_statements()
        except Consumer.ConsumingError as e:
            logger.error(e.message)

        total_pages = json_data.get('total_pages', 1)
        current_page += 1

        # Load data here
