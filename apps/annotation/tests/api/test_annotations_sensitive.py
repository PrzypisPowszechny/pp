import json
from django.test import TestCase
from model_mommy import mommy
from apps.annotation.tests.utils import create_test_user


class AnnotationAPITest(TestCase):
    base_url = "/api/annotations-sensitive"
    maxDiff = None

    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_empty_returns_200(self):
        response = self.client.post(
            self.base_url,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_body_params_filtering(self):
        mommy.make('annotation.Annotation', 1)
        response = self.client.post(
            self.base_url,
            json.dumps({'url': 'not-existing.url'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertEqual(len(response_content_data), 0)
