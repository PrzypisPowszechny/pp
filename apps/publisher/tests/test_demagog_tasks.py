import json
from datetime import timedelta
from urllib.parse import urlencode

import responses
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.utils import timezone

from apps.annotation.models import Annotation
from apps.publisher.demagog import sync_using_sources_list, demagog_to_pp_category

TEST_URL = 'http://i-test-you-all.org'
OTHER_URL = 'http://i-dont-test-anything.org'

SOURCE_URL = 'http://i-am-article-you-check.org'
SOURCE_URL2 = 'http://i-am-article-you-check-n2.org'
FACT_URL = 'http://i-check-you-all.org'


class DemagogTasksTest(TestCase):
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
    def test_sync_using_sources_list__one(self):
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
        sync_using_sources_list()
        self.assertEqual(Annotation.objects.count(), annotation_count + 1)
        # Do no re-add
        sync_using_sources_list()
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

    # TODO: this should be unit test of function responsible of comparing records, not whole functional test
    @responses.activate
    def test_sync_using_sources_list__two(self):
        statement_data = self.get_statement_valid_data()
        statement_attrs = statement_data['attributes']
        statement_data2 = self.get_statement_valid_data()
        statement_attrs2 = statement_data2['attributes']
        statement_data2['id'] = statement_data['id'] + 1
        statement_attrs2['source'] = SOURCE_URL2

        responses.add(responses.Response(
            method='GET',
            url="{}{}".format(settings.DEMAGOG_API_URL, self.get_sources_list_path),
            match_querystring=False,
            content_type='application/json',
            body=json.dumps({'data': {'attributes': {'sources': [SOURCE_URL, SOURCE_URL2]}}})
        ))

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path, urlencode({'uri': SOURCE_URL})),
            content_type='application/json',
            match_querystring=False,
            body=json.dumps({'data': [statement_data]}, cls=DjangoJSONEncoder)
        ))

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path, urlencode({'uri': SOURCE_URL2})),
            content_type='application/json',
            match_querystring=False,
            body=json.dumps({'data': [statement_data2]}, cls=DjangoJSONEncoder)
        ))

        annotation_count = Annotation.objects.count()
        sync_using_sources_list()
        self.assertEqual(Annotation.objects.count(), annotation_count + 2)
