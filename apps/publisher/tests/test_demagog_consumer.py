import json
from urllib.parse import urlencode

import responses
from django.conf import settings
from django.test import TestCase
from parameterized import parameterized

from apps.publisher.consumers import DemagogConsumer

TEST_URL = 'http://i-test-you-all.org'
OTHER_URL = 'http://i-dont-test-anything.org'


class DemagogAPITest(TestCase):
    maxDiff = None

    def setUp(self):
        pass

    get_all_statements_path = '/statements'
    get_statements_path = '/statements'
    get_sources_list_path = '/sources_list'

    @parameterized.expand([
        # Expected response - none error
        (1, {'page': 1}, json.dumps({'total_pages': 1, 'current_page': 1, 'data': []}),
         None),
        # Default page - none error
        (None, {'page': 1}, json.dumps({'total_pages': 1, 'current_page': 1, 'data': []}),
         None),
        # Malformed data
        (1, {'page': 1}, "xyz",
         DemagogConsumer.ConsumingResponseError),
        # Non existing page
        (2, {'page': 1}, json.dumps({'total_pages': 1, 'current_page': 1, 'data': []}),
         DemagogConsumer.ConsumingResponseError),
        # Data detailed validation failed
        (1, {'page': 1}, json.dumps({'total_pages': 1, 'current_page': 1, 'data': 'xyz'}),
         DemagogConsumer.ConsumingDataError),
        # Missing total_pages
        (1, {'page': 1}, json.dumps({'current_page': 1, 'data': []}),
         DemagogConsumer.ConsumingDataError),
        # Missing current
        (1, {'page': 1}, json.dumps({'total_pages': 1, 'data': []}),
         DemagogConsumer.ConsumingDataError),
        # Missing data
        (1, {'page': 1}, json.dumps({'total_pages': 1, 'current_page': 1}),
         DemagogConsumer.ConsumingDataError),
    ])
    @responses.activate
    def test_get_all_statements(self, *args):
        request_page, response_more_params, body, expected_error = args

        params = {'q': 'all', 'client': 'pp'}
        params.update(response_more_params)

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_all_statements_path, urlencode(params)),
            match_querystring=True,
            content_type='application/json',
            body=body
        ))

        run_get = lambda: DemagogConsumer().get_all_statements(*([request_page] if request_page is not None else []))

        if expected_error:
            with self.assertRaises(expected_error, msg='Error for args: {}'.format(args)):
                run_get()
        else:
            json_body = json.loads(body)
            self.assertEqual((json_body['total_pages'], json_body['current_page'], json_body['data']), run_get(),
                             msg='Error for args: {}'.format(args))

    @parameterized.expand([
        # Expected response - none error
        (TEST_URL, TEST_URL, json.dumps({'data': []}),
         None),
        # Malformed data
        (TEST_URL, TEST_URL, "xyz",
         DemagogConsumer.ConsumingResponseError),
        # Urls mismatch
        (TEST_URL, OTHER_URL, json.dumps({'data': []}),
         DemagogConsumer.ConsumingResponseError),
        # Data detailed validation failed
        (TEST_URL, TEST_URL, json.dumps({'data': 'xyz'}),
         DemagogConsumer.ConsumingDataError),
        # Missing data
        (TEST_URL, TEST_URL, json.dumps({}),
         DemagogConsumer.ConsumingDataError),
    ])
    @responses.activate
    def test_get_statements(self, *args):
        request_url, response_url, body, expected_error = args

        params = {'client': 'pp', 'uri': response_url}

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_statements_path, urlencode(params)),
            match_querystring=True,
            content_type='application/json',
            body=body
        ))

        run_get = lambda: DemagogConsumer().get_statements(request_url)

        if expected_error:
            with self.assertRaises(expected_error, msg='Error for args: {}'.format(args)):
                run_get()
        else:
            json_body = json.loads(body)
            self.assertEqual(json_body['data'], run_get(), msg='Error for args: {}'.format(args))

    @parameterized.expand([
        # Expected response - none error
        (json.dumps({'data': {'attributes': {'sources': []}}}),
         None),
        # Malformed data
        ('xyz',
         DemagogConsumer.ConsumingResponseError),
        # Data detailed validation failed
        (json.dumps({}),
         DemagogConsumer.ConsumingDataError),
        (json.dumps({'data': None}),
         DemagogConsumer.ConsumingDataError),
    ])
    @responses.activate
    def test_get_sources(self, *args):
        body, expected_error = args

        params = {'client': 'pp', }

        responses.add(responses.Response(
            method='GET',
            url="{}{}?{}".format(settings.DEMAGOG_API_URL, self.get_sources_list_path, urlencode(params)),
            match_querystring=True,
            content_type='application/json',
            body=body
        ))

        run_get = lambda: DemagogConsumer().get_sources_list()

        if expected_error:
            with self.assertRaises(expected_error, msg='Error for args: {}'.format(args)):
                run_get()
        else:
            json_body = json.loads(body)
            self.assertEqual(json_body['data']['attributes']['sources'], run_get(),
                             msg='Error for args: {}'.format(args))
