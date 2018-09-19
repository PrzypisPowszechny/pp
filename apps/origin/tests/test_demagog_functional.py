import json
from datetime import timedelta
from urllib.parse import urlencode

import responses
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.utils import timezone

from apps.annotation.models import Annotation
from apps.origin.demagog_consumer import consume_statements_from_sources_list, demagog_to_pp_category

TEST_URL = 'http://i-test-you-all.org'
OTHER_URL = 'http://i-dont-test-anything.org'

SOURCE_URL = 'http://i-am-article-you-check.org'
FACT_URL = 'http://i-check-you-all.org'


class DemagogAPITest(TestCase):
    maxDiff = None

    def setUp(self):
        pass

    get_all_statements_path = '/'
    get_statements_path = '/statements'
    get_sources_list_path = '/sources_list'

    def get_statement_valid_attrs(self):
        return {
            'source': SOURCE_URL,
            'text': "it's an interesting article",
            'date':  timezone.now() - timedelta(days=2),
            'rating': 'true',
            'rating_text': 'true statement',
            'factchecker_uri': FACT_URL
        }

    def get_statement_valid_data(self):
        return {
            'id': 1,
            'attributes': self.get_statement_valid_attrs()
        }

    @responses.activate
    def test_consume_statements_from_sources_list(self):
        statement_data = self.get_statement_valid_data()
        statement_attrs = statement_data['attributes']

        responses.add(responses.Response(
            method='GET',
            url="{}{}".format(settings.DEMAGOG_API_URL, self.get_sources_list_path),
            match_querystring=False,
            content_type='application/json',
            body=json.dumps({'data': {'attributes': {'sources': [SOURCE_URL]}}})
        ))

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path, urlencode({'uri': SOURCE_URL})),
            content_type='application/json',
            match_querystring=False,
            body=json.dumps({'data': [statement_data]}, cls=DjangoJSONEncoder)
        ))

        annotation_count = Annotation.objects.count()
        consume_statements_from_sources_list()
        self.assertEqual(Annotation.objects.count(), annotation_count + 1)
        annotation = Annotation.objects.last()
        self.assertEqual(annotation.publisher_annotation_id, statement_data['id'])
        self.assertEqual(annotation.url, statement_attrs['source'])
        self.assertEqual(annotation.pp_category, demagog_to_pp_category[statement_attrs['rating'].upper()])
        self.assertEqual(annotation.demagog_category, statement_attrs['rating'].upper())
        self.assertEqual(annotation.quote, statement_attrs['text'])
        self.assertEqual(annotation.annotation_link, statement_attrs['factchecker_uri'])
        # JSON converting is a bit inaccurate, so compare two json dates, to same inaccurate
        self.assertEqual(json.dumps(annotation.create_date, cls=DjangoJSONEncoder),
                         json.dumps(statement_attrs['date'], cls=DjangoJSONEncoder))
