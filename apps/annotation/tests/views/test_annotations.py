from django.test import TestCase
from mock import patch
from model_mommy import mommy
from parameterized import parameterized
from rest_framework.test import APIRequestFactory

from apps.annotation.models import Annotation
from apps.annotation.tests.utils import create_test_user
from apps.annotation.views.annotations import AnnotationList


class AnnotationViewTest(TestCase):
    maxDiff = None

    # We do not test request URL here and it should not play a role, so we use a fake URL for all requests
    mock_url = 'mock-url'

    def setUp(self):
        self.user, password = create_test_user()

    def request_to_generic_class_view(self, view_class, method, data=None, headers=None):
        factory = APIRequestFactory()
        # factory.post(...) / .get(...)
        request = getattr(factory, method)(self.mock_url, data)
        # mock session since it is expected by some processors
        request.session = self.client.session
        headers = headers or {}
        for key, val in headers.items():
            request.META[key] = val
        response = view_class.as_view()(request)
        results = response.data['results']
        return response, results

    def test_list_returns_200(self):
        response, results = self.request_to_generic_class_view(AnnotationList, 'get')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)

    def test_list_no_filtering_returns_all(self):
        mommy.make('annotation.Annotation')
        expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationList, 'get')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    filtering_test_params = [
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

    @parameterized.expand(filtering_test_params)
    def test_list_header_url_filtering(self, actual_url, query_url, expected_count):
        annotation = mommy.make('annotation.Annotation')
        annotation.url = actual_url
        annotation.save()

        if expected_count == 'all':
            expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationList, 'get', headers={
            'HTTP_PP_SITE_URL': query_url,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    @parameterized.expand(filtering_test_params)
    def test_list_param_url_filtering(self, actual_url, query_url, expected_count):
        annotation = mommy.make('annotation.Annotation')
        annotation.url = actual_url
        annotation.save()

        if expected_count == 'all':
            expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationList, 'get', data={'url': query_url})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    # Pagination is out of the box with DRF, but it is actually something important...
    def test_list_returns_limited(self):
        mommy.make('annotation.Annotation', 10)
        all_count = Annotation.objects.count()

        # patch PAGE_SIZE so as not to have to create > 100 Annotations...
        with patch('rest_framework.pagination.LimitOffsetPagination.default_limit', 5):
            response, results = self.request_to_generic_class_view(AnnotationList, 'get')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertLess(len(results), all_count)
