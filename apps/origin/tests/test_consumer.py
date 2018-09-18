import json

import responses
from django.test import TestCase
from parameterized import parameterized

from apps.origin.consumer import Consumer

TEST_URL = 'http://i-test-you-all.org'
OTHER_URL = 'http://i-dont-test-anything.org'


class TestConsumer(Consumer):
    api_name = 'Test API'
    base_url = TEST_URL


class AnnotationAPITest(TestCase):
    maxDiff = None

    def setUp(self):
        pass

    @parameterized.expand([
        (TEST_URL, 200,  json.dumps({'test_key': 'test_value'}),
         True),
        (TEST_URL, 200, json.dumps({}),
         True),
        (TEST_URL, 404, json.dumps({'test_key': 'test_value'}),
         False),
        (TEST_URL, 500, json.dumps({'test_key': 'test_value'}),
         False),
        (TEST_URL, 200, "plaintext",
         False),
        # This is test for connection error, when there is no response
        (OTHER_URL, 200, json.dumps({}),
         False),
    ])
    @responses.activate
    def test_get(self, *args):
        url, status_code, body, positive_result = args

        responses.add(responses.Response(
            method='GET',
            url=url,
            content_type='application/json',
            status=status_code,
            body=body
        ))

        run_get = lambda: TestConsumer().get('/')

        if positive_result:
            json_data = run_get()
            self.assertEqual(json.loads(body), json_data, msg='Error for args: {}'.format(json.dumps(args)))
        else:
            with self.assertRaises(Consumer.ConsumingResponseError, msg='Error for args: {}'.format(json.dumps(args))):
                run_get()
