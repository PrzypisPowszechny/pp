import responses
from django.conf import settings
from django.test import TestCase
from mock import patch
from model_mommy import mommy
from parameterized import parameterized
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.models import Annotation
from apps.annotation.tasks import notify_annotation_url_subscribers
from apps.annotation.tests.utils import create_test_user
from apps.annotation.views.annotations import AnnotationViewSet
from worker import celery_app


class AnnotationViewTest(TestCase):
    maxDiff = None

    # We do not test request URL here and it should not play a role, so we use a fake URL for all requests
    mock_url = 'mock-url'

    actions = {
        'get': 'list',
        'post': 'create',
    }

    def setUp(self):
        self.user, password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token
        Annotation.objects.all().update(check_status=Annotation.UNVERIFIED)

    def request_to_generic_class_view(self, view_class, method, data=None, headers=None):
        factory = APIRequestFactory()
        # factory.post(...) / .get(...)
        request = getattr(factory, method)(self.mock_url, data)

        headers = headers or {}
        headers['HTTP_AUTHORIZATION'] = self.token_header
        for key, val in headers.items():
            request.META[key] = val
        response = view_class.as_view({method: self.actions[method]})(request)
        if method == 'get':
            results = response.data['results']
        else:
            results = response.data
        return response, results

    def test_list_returns_200(self):
        response, results = self.request_to_generic_class_view(AnnotationViewSet, 'get')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)

    def test_list_no_filtering_returns_all(self):
        mommy.make('annotation.Annotation')
        expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationViewSet, 'get')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

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
        annotation = mommy.make('annotation.Annotation')
        annotation.url = actual_url
        annotation.save()

        if expected_count == 'all':
            expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationViewSet, 'get', headers={
            'HTTP_PP_SITE_URL': query_url,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    @parameterized.expand(filtering_url_test_params)
    def test_list_param_url_filtering(self, actual_url, query_url, expected_count):
        annotation = mommy.make('annotation.Annotation')
        annotation.url = actual_url
        annotation.save()

        if expected_count == 'all':
            expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationViewSet, 'get', data={'url': query_url})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    @parameterized.expand([
        # No filtering - include
        (Annotation.CONFIRMED,
         '',
         'all'),
        # Exact - include
        (Annotation.CONFIRMED,
         Annotation.CONFIRMED,
         1),
        # Different
        (Annotation.UNLOCATABLE,
         Annotation.CONFIRMED,
         0),
    ])
    def test_list_check_status_filtering(self, actual_status, query_status, expected_count):
        # Relies on setUp UNVERIFIED value
        annotation = mommy.make('annotation.Annotation')
        annotation.check_status = actual_status
        annotation.save()

        if expected_count == 'all':
            expected_count = Annotation.objects.count()

        response, results = self.request_to_generic_class_view(AnnotationViewSet, 'get',
                                                               data={'check_status': query_status})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), expected_count)

    # Pagination is out of the box with DRF, but it is actually something important...
    def test_list_returns_limited(self):
        mommy.make('annotation.Annotation', 10)
        all_count = Annotation.objects.count()

        # patch PAGE_SIZE so as not to have to create > 100 Annotations...
        with patch('rest_framework.pagination.LimitOffsetPagination.default_limit', 5):
            response, results = self.request_to_generic_class_view(AnnotationViewSet, 'get')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(results)
        self.assertLess(len(results), all_count)

    def get_valid_annotation_attrs(self):
        return {
            'url': "http://www.przypis.pl/",
            'range': {'start': "Od tad", 'end': "do tad"},
            'quote': 'very nice',
            'quoteContext': 'it is indeed very nice and smooth',
            'publisher': 'PP',
            'ppCategory': Annotation.ADDITIONAL_INFO,
            'comment': "komentarz",
            'annotationLink': 'www.przypispowszechny.com',
            'annotationLinkTitle': 'very nice too',
        }

    def get_valid_request_template(self):
        return {
            'data': {
                'type': 'annotations',
                'attributes': self.get_valid_annotation_attrs()
            }
        }


class AnnotationTaskTest(AnnotationViewTest):

    def test_notify_subscribers_scheduled_imported(self):
        self.assertIn('apps.annotation.tasks.notify_annotation_url_subscribers', celery_app.tasks)

    @responses.activate
    def test_notify_subscribers_scheduled(self):
        site_url = 'https://www.mocksite.com'

        data = self.get_valid_request_template()
        data['data']['attributes']['url'] = site_url

        with patch('apps.annotation.signals.notify_annotation_url_subscribers') as task_mock:
            response, results = self.request_to_generic_class_view(AnnotationViewSet, 'post', data=data)
            self.assertEqual(response.status_code, 201)
            self.assertIsNotNone(results)
            annotation_id = int(results['id'])
            task_mock.apply_async.assert_called_once_with(args=[annotation_id])

    @responses.activate
    def test_subscribers_notified(self):
        notification_email = 'test@gmail.com'
        site_url = 'https://www.mocksite.com'

        responses.add(responses.Response(
            method='POST',
            url=settings.MAILGUN_API_URL,
            match_querystring=True,
            content_type='application/json',
            status=200,
        ))

        annotation_request = mommy.make('annotation.AnnotationRequest')
        annotation_request.notification_email = notification_email
        annotation_request.url = site_url
        annotation_request.save()

        data = self.get_valid_request_template()
        data['data']['attributes']['url'] = site_url

        with patch('apps.annotation.signals.notify_annotation_url_subscribers') as task_mock:
            annotation = mommy.make('annotation.Annotation', url=site_url)
            annotation.save()
            task_mock.apply_async.assert_called_once_with(args=[annotation.id])

        notify_annotation_url_subscribers(annotation.id)

        self.assertEqual(len(responses.calls), 1)
