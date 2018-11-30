import json
from datetime import timedelta
from urllib.parse import urlencode

import responses
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from parameterized import parameterized

from apps.annotation.models import Annotation
from apps.publisher.demagog import sync_using_sources_list, demagog_to_pp_category, update_or_create_annotation
from apps.publisher.tests.demagog_test_case import DemagogTestCase


class DemagogTasksTest(DemagogTestCase):
    get_all_statements_path = '/statements'
    get_statements_path = '/statements'
    get_sources_list_path = '/sources_list'

    @responses.activate
    def test_sync_using_sources_list__one(self):
        statement_data = self.get_statement_valid_data()
        statement_attrs = statement_data['attributes']

        responses.add(responses.Response(
            method='GET',
            url="{}{}".format(settings.DEMAGOG_API_URL, self.get_sources_list_path),
            match_querystring=False,
            content_type='application/json',
            body=json.dumps({'data': {'attributes': {'sources': [self.SOURCE_URL]}}})
        ))

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path,
                                 urlencode({'uri': self.SOURCE_URL})),
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
        self.assertEqual(annotation.url, statement_attrs['sources'][0])
        self.assertEqual(annotation.pp_category, demagog_to_pp_category[statement_attrs['rating'].upper()])
        self.assertEqual(annotation.demagog_category, statement_attrs['rating'].upper())
        self.assertEqual(annotation.quote, statement_attrs['text'])
        self.assertEqual(annotation.annotation_link, statement_attrs['factchecker_uri'])
        # JSON converting is a bit inaccurate, so compare two json dates, to same inaccurate
        self.assertEqual(json.dumps(annotation.create_date, cls=DjangoJSONEncoder),
                         json.dumps(statement_attrs['timestamp_factcheck'], cls=DjangoJSONEncoder))

    # TODO: this should be unit test of function responsible of comparing records, not whole functional test
    @responses.activate
    def test_sync_using_sources_list__two(self):
        statement_data = self.get_statement_valid_data()
        statement_attrs = statement_data['attributes']
        statement_data2 = self.get_statement_valid_data()
        statement_attrs2 = statement_data2['attributes']
        statement_data2['id'] = statement_data['id'] + '_anything_different'
        statement_attrs2['source'] = self.SOURCE_URL2

        responses.add(responses.Response(
            method='GET',
            url="{}{}".format(settings.DEMAGOG_API_URL, self.get_sources_list_path),
            match_querystring=False,
            content_type='application/json',
            body=json.dumps({'data': {'attributes': {'sources': [self.SOURCE_URL, self.SOURCE_URL2]}}})
        ))

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path,
                                 urlencode({'uri': self.SOURCE_URL})),
            content_type='application/json',
            match_querystring=False,
            body=json.dumps({'data': [statement_data]}, cls=DjangoJSONEncoder)
        ))

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path,
                                 urlencode({'uri': self.SOURCE_URL2})),
            content_type='application/json',
            match_querystring=False,
            body=json.dumps({'data': [statement_data2]}, cls=DjangoJSONEncoder)
        ))

        annotation_count = Annotation.objects.count()
        sync_using_sources_list()
        self.assertEqual(Annotation.objects.count(), annotation_count + 2)

    # TODO: create specialized tests for less standard cases, this is basic test of mapping and should remain simple
    @parameterized.expand([
        [{}],
        # Test that create_date is demagog create_date, not out insert date
        [{'timestamp_factcheck': timezone.now() - timedelta(days=2)}],
    ])
    def test_update_or_create_annotation__general_fields_mapping(self, override_attrs):
        statement_data = self.get_statement_valid_data()
        statement_data['attributes'].update(override_attrs)
        attrs = statement_data['attributes']
        annotation = update_or_create_annotation(statement_data=statement_data)

        self.assertTrue(annotation)
        self.assertEqual(annotation.publisher, annotation.DEMAGOG_PUBLISHER)
        self.assertEqual(annotation.publisher_annotation_id, statement_data['id'])
        self.assertEqual(annotation.url, attrs['sources'][0])
        self.assertEqual(annotation.pp_category, demagog_to_pp_category[attrs['rating'].upper()])
        self.assertEqual(annotation.demagog_category, attrs['rating'].upper())
        self.assertEqual(annotation.annotation_link, attrs['factchecker_uri'])
        self.assertEqual(annotation.comment, attrs['explanation'])
        self.assertEqual(annotation.create_date, attrs['timestamp_factcheck'])
