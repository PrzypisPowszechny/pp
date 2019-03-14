import responses
from django.conf import settings
from django.test import TestCase
from parameterized import parameterized
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.tests.utils import create_test_user, merge
from apps.annotation.views.annotation_requests import AnnotationRequestList


class AnnotationRequestsViewTest(TestCase):
    maxDiff = None

    # We do not test request URL here and it should not play a role, so we use a fake URL for all requests
    mock_url = 'mock-url'

    def setUp(self):
        self.user, password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token

    def request_to_class_view(self, view_class, method, data=None, headers=None):
        factory = APIRequestFactory()
        # factory.post(...) / .get(...)
        request = getattr(factory, method)(self.mock_url, data)

        headers = headers or {}
        headers['HTTP_AUTHORIZATION'] = self.token_header
        for key, val in headers.items():
            request.META[key] = val
        response = view_class.as_view()(request)
        return response

    @staticmethod
    def request_template():
        return {
            'data': {
                'type': 'annotation_requests',
                'attributes': {}
            }
        }

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl'}}},),
    ])
    @responses.activate
    def test_post_200(self, data):
        # mock email response
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))
        request_data = self.request_template()
        merge(request_data, data)

        response = self.request_to_class_view(AnnotationRequestList, 'post', data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response)

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl/', 'notification_email': 'abc@test.pl'}}},),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl/', 'comment': 'komentarz'}}},),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl/', 'quote': 'fragment tekstu'}}},),
    ])
    @responses.activate
    def test_post_optional_string_attributes(self, data):
        # mock email response
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))
        request_data = self.request_template()
        merge(request_data, data)

        response = self.request_to_class_view(AnnotationRequestList, 'post', data=request_data)
        for send_attr, send_value in data['data']['attributes'].items():
            self.assertEqual(send_value, response.data['attributes'].get(send_attr, ''))

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl'}}}, 'http://www.xyz.pl/'),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl#xyz'}}}, 'http://www.xyz.pl/'),
    ])
    @responses.activate
    def test_url_standardized(self, data, expected_response_url):
        # mock email response
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))
        request_data = self.request_template()
        merge(request_data, data)

        response = self.request_to_class_view(AnnotationRequestList, 'post', data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response)
        self.assertEqual(response.data['attributes']['url'], expected_response_url)

    @responses.activate
    def test_error_logged(self):
        data = {'data': {'attributes': {'url': 'http://www.xyz.pl'}}}

        # mock email response
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=400,
        ))

        request_data = self.request_template()
        merge(request_data, data)

        with self.assertLogs('pp.annotation', level='ERROR') as cm:
            response = self.request_to_class_view(AnnotationRequestList, 'post', data=request_data)
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response)
            self.assertEqual(len(cm.output), 1)
