import json

from django.test import TestCase

from apps.pp.models import Annotation
from apps.pp.tests.utils import create_test_user


class AnnotationUpvoteAPITest(TestCase):
    user_single_url = "/api/users/{}"
    annotation_related_user_url = "/api/annotations/{}/user"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_user(self):
        # Add annotation to make sure that despite existing relation, no relationships in the response
        # (we do not expose it from user side)
        Annotation.objects.create(user=self.user)

        response = self.client.get(self.user_single_url.format(self.user.id),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(self.user.id),
                'type': 'users',
                'attributes': {}
            }}
        )

        response = self.client.get(self.user_single_url.format(self.user.id + 1),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

    def test_get_annotation_related_user(self):
        annotation = Annotation.objects.create(user=self.user)

        response = self.client.get(self.annotation_related_user_url.format(annotation.id),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(self.user.id),
                'type': 'users',
                'attributes': {}
            }}
        )

        response = self.client.get(self.annotation_related_user_url.format(annotation.id + 1),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)
