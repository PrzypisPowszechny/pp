import json

from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.models import Annotation
from apps.annotation.tests.utils import create_test_user


class AnnotationUpvoteAPITest(TestCase):
    user_single_url = "/api/users/{}"
    annotation_related_user_url = "/api/annotations/{}/user"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token

    def test_get_user__active(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.get(self.user_single_url.format(self.user.id),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode())['data']['id'], str(self.user.id))

    def test_get_user__non_existing(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.get(self.user_single_url.format(self.user.id + 1),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 404)

    def test_get_annotation_related_user__inactive(self):
        annotation = Annotation.objects.create(user=self.user)
        self.user.is_active = False
        self.user.save()

        response = self.client.get(self.annotation_related_user_url.format(annotation.id),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 401)

    def test_get_annotation_related_user(self):
        annotation = Annotation.objects.create(user=self.user)
        self.user.is_active = True
        self.user.save()

        response = self.client.get(self.annotation_related_user_url.format(annotation.id),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode())['data']['id'], str(self.user.id))

    def test_get_annotation_related_user__not_found(self):
        annotation = Annotation.objects.create(user=self.user)
        self.user.is_active = True
        self.user.save()

        response = self.client.get(self.annotation_related_user_url.format(annotation.id + 1),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 404)
