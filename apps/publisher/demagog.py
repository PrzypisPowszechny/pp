import logging
from collections import defaultdict

import bleach
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import Truncator

from worker import celery_app
from apps.annotation.models import Annotation
from .consumers import DemagogConsumer

logger = logging.getLogger('pp.publisher')


UNCHANGED = 'unchanged'
CREATED = 'created'
UPDATED = 'updated'
FAILED = 'failed'


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

    annotation_stats = defaultdict(int)
    consuming_errors = 0
    demagog_user = get_user_model().objects.get(username=settings.DEMAGOG_USERNAME)
    for source_url in sources_list:
        try:
            statements = consumer.get_statements(source_url)
        except DemagogConsumer.ConsumingError as e:
            logger.warning(str(e))
            consuming_errors += 1
        else:
            for statement_data in statements:
                annotation, action_applied = update_or_create_annotation(statement_data, demagog_user)
                annotation_stats[action_applied] += 1
    logger.info('Consumed {sources_num} sources with {errors_num} errors, annotations created/updated: {stats}'.format(
        sources_num=len(sources_list),
        errors_num=consuming_errors,
        stats=",".join('%s=%s' % (k, v) for k, v in annotation_stats.items()))
    )


def update_or_create_annotation(statement_data, demagog_user=None):
    statement_attrs = statement_data['attributes']
    demagog_user = demagog_user or get_user_model().objects.get(username=settings.DEMAGOG_USERNAME)
    annotation_fields = statement_attrs_to_annotation_fields(statement_attrs)

    annotation, created = Annotation.objects.get_or_create(
        publisher=Annotation.DEMAGOG_PUBLISHER,
        publisher_annotation_id=statement_data['id'],
        defaults=dict(
            user=demagog_user,
            _history_user=demagog_user,
            **annotation_fields
        )
    )

    if created:
        action = 'created'
        status = CREATED
    else:
        changed = False
        for key, val in annotation_fields.items():
            if getattr(annotation, key) != val:
                setattr(annotation, key, val)
                changed = True
        if changed:
            action = 'changed'
            status = UPDATED
            annotation._history_user = demagog_user
            annotation.save()
        else:
            action = 'ignored (unchanged)'
            status = UNCHANGED

    logger.debug('Annotation with demagog id=%s was: %s' % (statement_data['id'], action))
    return annotation, status


def statement_attrs_to_annotation_fields(attrs):
    vals = {
        'url': attrs['sources'][0],
        'pp_category': demagog_to_pp_category[attrs['rating'].upper()],
        'demagog_category': attrs['rating'].upper(),
        'quote': attrs['text'],
        'annotation_link': attrs['factchecker_uri'],
        'comment': get_first_paragraph(attrs['explanation']),
        'annotation_link_title': 'Weryfikacja opracowana przez zespół Demagoga',
        'create_date': attrs.get('timestamp_factcheck'),
    }
    return {key: val for key, val in vals.items() if val is not None}


def get_first_paragraph(explanation):
    # TODO: when format of explanation is known implement this function as needed by finding \n or <br/> or </div> etc
    # Use bleach to get rid of html tags 100% safely
    return Truncator(bleach.clean(explanation, tags=[], strip=True)).chars(400)


demagog_to_pp_category = {
    Annotation.TRUE: Annotation.ADDITIONAL_INFO,
    Annotation.PTRUE: Annotation.ADDITIONAL_INFO,
    Annotation.FALSE: Annotation.ERROR,
    Annotation.PFALSE: Annotation.ERROR,
    Annotation.LIE: Annotation.CLARIFICATION,
    Annotation.UNKOWN: Annotation.ADDITIONAL_INFO,
}
