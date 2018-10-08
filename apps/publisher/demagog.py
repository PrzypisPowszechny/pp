import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from worker import celery_app
from apps.annotation.models import Annotation
from .consumers import DemagogConsumer

logger = logging.getLogger('pp.publisher')


@celery_app.task
def sync_using_all_statements():
    consumer = DemagogConsumer()

    demagog_user = get_user_model().objects.get(username=settings.DEMAGOG_USERNAME)
    current_page = 0
    total_pages = 0

    while True:
        current_page += 1

        logger.info('Consuming page {} of {}'.format(current_page, total_pages or 'unknown'))
        try:
            total_pages, current_page_ignored, statements = consumer.get_all_statements()
        except DemagogConsumer.ConsumingError as e:
            logger.warning(str(e))
        else:
            for statement_data in statements:
                update_or_create_annotation(statement_data, demagog_user)
        if current_page >= total_pages:
            break


@celery_app.task
def sync_using_sources_list():
    consumer = DemagogConsumer()

    try:
        sources_list = consumer.get_sources_list()
    except DemagogConsumer.ConsumingError as e:
        logger.warning(str(e))
        return

    if not sources_list:
        logger.warning('Sources list is empty')
    else:
        logger.info('Starting iteration over %s sources' % len(sources_list))

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

    if created:
        action = 'created'
    else:
        changed = False
        for key, val in annotation_fields.items():
            if getattr(annotation, key) != val:
                setattr(annotation, key, val)
                changed = True
        if changed:
            action = 'changed'
            annotation._history_user = demagog_user
            annotation.save()
        else:
            action = 'ignored'

    logger.info('Annotation with demagog id=%s was: %s' % (statement_data['id'], action))


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
