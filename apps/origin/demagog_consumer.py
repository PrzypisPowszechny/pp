import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from apps.annotation.models import Annotation
from .consumer import Consumer
from .serializers import StatementDeserializer, SourcesDeserializer

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
        return deserializer.validated_data

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

    demagog_user = get_user_model().objects.get(username=settings.DEMAGOG_USERNAME)
    current_page = 0
    total_pages = None

    while True:
        current_page += 1

        logger.info('Consuming page {} of {}'.format(current_page, total_pages or 'unknown'))
        try:
            total_pages, current_page_ignored, statements = consumer.get_all_statements()
        except Consumer.ConsumingError as e:
            logger.error(str(e))
        else:
            for statement_data in statements:
                update_or_create_annotation(statement_data, demagog_user)
        if current_page >= total_pages:
            break


def consume_statements_from_sources_list():
    consumer = DemagogConsumer()

    try:
        sources_list = consumer.get_sources_list()
    except Consumer.ConsumingError as e:
        logger.error(str(e))
        return

    demagog_user = get_user_model().objects.get(username=settings.DEMAGOG_USERNAME)
    for source_url in sources_list:
        statements = consumer.get_statements(source_url)
        for statement_data in statements:

            update_or_create_annotation(statement_data, demagog_user)


def update_or_create_annotation(statement_data, demagog_user=None):
    statement_attrs = statement_data['attributes']
    demagog_user = demagog_user or get_user_model().objects.get(username=settings.DEMAGOG_USERNAME)
    annotation_fields = statement_attrs_to_annotation_fields(statement_attrs)

    annotation, created = Annotation.objects.get_or_create(
        publisher=Annotation.DEMAGOG_PUBLISHER,
        publisher_annotation_id=statement_data['id'],
        defaults=dict(
            user=demagog_user,
            _history_user= demagog_user,
            **annotation_fields
        )
    )

    if not created:
        changed = False
        for key, val in annotation_fields:
            if getattr(annotation, key) != val:
                setattr(annotation, key, val)
                changed = True
        if changed:
            annotation._history_user = demagog_user
            annotation.save()


def statement_attrs_to_annotation_fields(attrs):
    return {
        'url': attrs['source'],
        'pp_category': demagog_to_pp_category[attrs['rating'].upper()],
        'demagog_category': attrs['rating'].upper(),
        'quote': attrs['text'],
        'annotation_link': attrs['factchecker_uri'],
        # TODO: what should be the title?
        'annotation_link_title': 'Demagog.org.pl',
        'create_date': attrs['date'],
    }


demagog_to_pp_category = {
    Annotation.TRUE: Annotation.ADDITIONAL_INFO,
    Annotation.PTRUE: Annotation.ADDITIONAL_INFO,
    Annotation.FALSE: Annotation.ERROR,
    Annotation.PFALSE: Annotation.ERROR,
    Annotation.LIE: Annotation.CLARIFICATION,
    Annotation.UNKOWN: Annotation.CLARIFICATION,
}
