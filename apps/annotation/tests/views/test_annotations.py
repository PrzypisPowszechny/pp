from django.test import TestCase
from model_mommy import mommy
from parameterized import parameterized
from rest_framework.test import APIRequestFactory

from apps.annotation.models import Annotation
from apps.annotation.tests.utils import create_test_user
from apps.annotation.views.annotations import AnnotationListSensitive


class AnnotationViewTest(TestCase):
    maxDiff = None

    # We do not test request URL here and it should not play a role, so we use a fake URL for all requests
    mock_url = 'mock-url'

    def setUp(self):
        self.user, password = create_test_user()

    def request_to_class_view(self, view_class, method, data=None):
        factory = APIRequestFactory()
        # factory.post(...) / .get(...)
        request = getattr(factory, method)(self.mock_url, data)
        # mock session since it is expected by some processors
        request.session = self.client.session
        response = view_class.as_view()(request)
        results = response.data['results']
        return response, results

    def test_list_post_returns_200(self):
        response, results = self.request_to_class_view(AnnotationListSensitive, 'post')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)

    def test_list_post_no_filtering_returns_all(self):
        annotation = mommy.make('annotation.Annotation')
        annotation.save()

        expected_count = Annotation.objects.count()

        response, results = self.request_to_class_view(AnnotationListSensitive, 'post')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    @parameterized.expand([
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
    ])
    def test_list_post_filtering(self, actual_url, query_url, expected_count):
        annotation = mommy.make('annotation.Annotation')
        annotation.url = actual_url
        annotation.save()

        if expected_count == 'all':
            expected_count = Annotation.objects.count()

        response, results = self.request_to_class_view(AnnotationListSensitive, 'post', {'url': query_url})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)
