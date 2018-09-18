import json
from datetime import timedelta
from urllib.parse import quote

import responses
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_text
from model_mommy import mommy
from parameterized import parameterized
from rest_framework import serializers

from apps.annotation import consts
from apps.annotation.models import Annotation, AnnotationUpvote, AnnotationReport
from apps.annotation.tests.utils import create_test_user, testserver_reverse
from apps.origin.demagog_consumer import DemagogConsumer


class AnnotationAPITest(TestCase):
    maxDiff = None

    def setUp(self):
        pass

    @parameterized.expand([
        # No filtering - include
        ("/", 200, json.dumps({'test_key': 'test_value'}),
         True),
        ("/", 200, json.dumps({}),
         True),
        ("/", 404, json.dumps({'test_key': 'test_value'}),
         False),
        ("/", 500, json.dumps({'test_key': 'test_value'}),
         False),
        ("/", 200, "plaintext",
         False),
    ])
    @responses.activate
    def test_list_annotations__url_filtering(self, endpoint_path, status_code, body, is_correct):
        args = [endpoint_path, status_code, body, is_correct]
        responses.add(responses.Response(
            method='GET',
            url="{}{}".format(settings.DEMAGOG_API_URL, endpoint_path),
            match_querystring=False,
            content_type='application/json',
            status=status_code,
            body=body
        ))

        if not is_correct:
            with self.assertRaises(DemagogConsumer.ConsumingError, msg='Error for args: {}'.format(json.dumps(args))):
                DemagogConsumer().get_all_statements()
        else:
            json_data = DemagogConsumer().get_all_statements()
            self.assertEqual(json.loads(body), json_data, msg='Error for args: {}'.format(json.dumps(args)))
