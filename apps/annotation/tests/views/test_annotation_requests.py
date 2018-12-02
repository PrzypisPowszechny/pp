import responses
from django.conf import settings
from django.test import TestCase
from parameterized import parameterized
from rest_framework.test import APIRequestFactory

from apps.annotation.tests.utils import create_test_user
from apps.annotation.views.annotation_requests import AnnotationRequests


class AnnotationRequestsViewTest(TestCase):
    maxDiff = None

    # We do not test request URL here and it should not play a role, so we use a fake URL for all requests
    mock_url = 'mock-url'

    def setUp(self):
        self.user, password = create_test_user()

    def request_to_class_view(self, view_class, method, data=None, headers=None):
        factory = APIRequestFactory()
        # factory.post(...) / .get(...)
        request = getattr(factory, method)(self.mock_url, data)
        # mock session since it is expected by some processors
        request.session = self.client.session
        headers = headers or {}
        for key, val in headers.items():
            request.META[key] = val
        response = view_class.as_view()(request)
        return response

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl', 'quote': 'fragment tekstu'}}},),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl'}}},),
    ])
    @responses.activate
    def test_post_200(self, data):
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))
        response = self.request_to_class_view(AnnotationRequests, 'post', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response)

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl'}}}, 'http://www.xyz.pl/'),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl#xyz'}}}, 'http://www.xyz.pl/'),
    ])
    @responses.activate
    def test_url_standardized(self, data, expected_response_url):
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))
        response = self.request_to_class_view(AnnotationRequests, 'post', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response)
        self.assertEqual(response.data['attributes']['url'], expected_response_url)

    @responses.activate
    def test_error_logged(self):
        data = {'data': {'attributes': {'url': 'http://www.xyz.pl'}}}
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=400,
        ))

        with self.assertLogs('pp.annotation', level='ERROR') as cm:
            response = self.request_to_class_view(AnnotationRequests, 'post', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response)
            self.assertEqual(len(cm.output), 1)
