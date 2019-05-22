import json

import responses
from django.conf import settings
from django.test import TestCase
from model_mommy import mommy
from parameterized import parameterized
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.models import AnnotationRequest
from apps.annotation.tests.utils import create_test_user, merge
from apps.annotation.views.annotation_requests import AnnotationRequestViewSet


class AnnotationRequestViewSetTestCase(TestCase):
    maxDiff = None

    # We do not test request URL here and it should not play a role, so we use a fake URL for all requests
    mock_url = 'mock-url'

    actions = {
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
    }

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
        response = view_class.as_view({method: self.actions[method]})(request)
        response.render()
        return response

    @staticmethod
    def request_template():
        return {
            'data': {
                'type': 'annotationRequests',
                'attributes': {
                    'quote': 'earth is flat'
                }
            }
        }

    def mock_mailgun_response(self, status=200):
        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=status,
        ))

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl'}}},),
    ])
    @responses.activate
    def test_post_200(self, data):
        self.mock_mailgun_response()

        request_data = self.request_template()
        merge(request_data, data)

        response = self.request_to_class_view(AnnotationRequestViewSet, 'post', data=request_data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response)

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl/', 'notificationEmail': 'abc@test.pl'}}},),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl/', 'comment': 'komentarz'}}},),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl/', 'quote': 'fragment tekstu'}}},),
    ])
    @responses.activate
    def test_post_optional_string_attributes(self, data):
        self.mock_mailgun_response()
        request_data = self.request_template()
        merge(request_data, data)

        response = self.request_to_class_view(AnnotationRequestViewSet, 'post', data=request_data)
        self.assertEqual(response.status_code, 201, response.content.decode())
        for send_attr, send_value in data['data']['attributes'].items():
            self.assertEqual(send_value, json.loads(response.content.decode())['data']['attributes'].get(send_attr, ''),
                             response.content)

    @parameterized.expand([
        ({'data': {'attributes': {'url': 'http://www.xyz.pl'}}}, 'http://www.xyz.pl/'),
        ({'data': {'attributes': {'url': 'http://www.xyz.pl#xyz'}}}, 'http://www.xyz.pl/'),
    ])
    @responses.activate
    def test_url_standardized(self, data, expected_response_url):
        self.mock_mailgun_response()
        request_data = self.request_template()
        merge(request_data, data)

        response = self.request_to_class_view(AnnotationRequestViewSet, 'post', data=request_data)
        self.assertEqual(response.status_code, 201, response.content.decode())
        self.assertIsNotNone(response)
        self.assertEqual(json.loads(response.content.decode())['data']['attributes']['url'], expected_response_url)

    filtering_url_test_params = [
        # No filtering - include
        ("https://docs.python.org/",
         "",
         'all'),
        # Exact - include
        ("https://docs.python.org/",
         "https://docs.python.org/",
         1),
        # Different - exclude
        ("https://docs.python.org/",
         "https://github.com",
         0),
    ]

    @parameterized.expand(filtering_url_test_params)
    def test_list_header_url_filtering(self, actual_url, query_url, expected_count):
        annotation_request = mommy.make('annotation.AnnotationRequest')
        annotation_request.url = actual_url
        annotation_request.save()

        if expected_count == 'all':
            expected_count = AnnotationRequest.objects.count()

        response = self.request_to_class_view(AnnotationRequestViewSet, 'get', headers={
            'HTTP_PP_SITE_URL': query_url,
        })
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    @parameterized.expand(filtering_url_test_params)
    def test_list_param_url_filtering(self, actual_url, query_url, expected_count):
        annotation_request = mommy.make('annotation.AnnotationRequest')
        annotation_request.url = actual_url
        annotation_request.save()

        if expected_count == 'all':
            expected_count = AnnotationRequest.objects.count()

        response = self.request_to_class_view(AnnotationRequestViewSet, 'get', data={'url': query_url})
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    @responses.activate
    def test_error_logged(self):
        data = {'data': {'attributes': {'url': 'http://www.xyz.pl'}}}

        self.mock_mailgun_response(400)

        request_data = self.request_template()
        merge(request_data, data)

        with self.assertLogs('pp.annotation', level='ERROR') as cm:
            response = self.request_to_class_view(AnnotationRequestViewSet, 'post', data=request_data)
            self.assertEqual(response.status_code, 201)
            self.assertIsNotNone(response)
            self.assertEqual(len(cm.output), 1)

    @responses.activate
    def test_error_logged(self):
        data = {'data': {'attributes': {'url': 'http://www.xyz.pl'}}}

        self.mock_mailgun_response(400)

        request_data = self.request_template()
        merge(request_data, data)

        with self.assertLogs('pp.annotation', level='ERROR') as cm:
            response = self.request_to_class_view(AnnotationRequestViewSet, 'post', data=request_data)
            self.assertEqual(response.status_code, 201)
            self.assertIsNotNone(response)
            self.assertEqual(len(cm.output), 1)
