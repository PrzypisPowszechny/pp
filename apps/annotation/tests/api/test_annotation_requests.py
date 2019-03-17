import json

from django.test import TestCase
from model_mommy import mommy
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation import models
from apps.annotation.tests.utils import create_test_user


class AnnotationRequestListGet(TestCase):
    base_url = "/api/annotationRequests"
    maxDiff = None

    def setUp(self):
        self.user, self.password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token

    def test_get_200(self):
        mommy.make('annotation.AnnotationRequest')
        mommy.make('annotation.AnnotationRequest')

        response = self.client.get(self.base_url, HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf8'))
        self.assertEqual(len(response_data['data']), 2)


class AnnotationRequestSingle(TestCase):
    base_url = "/api/annotationRequests/{}"
    maxDiff = None

    def setUp(self):
        self.user, self.password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token

    def test_delete_200(self):
        annotation_request = mommy.make('annotation.AnnotationRequest', user=self.user)
        annotation_request_count = models.AnnotationRequest.objects.count()

        self.assertTrue(annotation_request.active)

        response = self.client.delete(self.base_url.format(annotation_request.id), HTTP_AUTHORIZATION=self.token_header)
        annotation_request.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.AnnotationRequest.objects.count(), annotation_request_count)
        self.assertFalse(annotation_request.active)

        # Return same result as if it never existed
        response = self.client.delete(self.base_url.format(annotation_request.id), HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 404)
