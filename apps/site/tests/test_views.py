from django.core.signing import Signer
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from apps.annotation.models import AnnotationRequest
from apps.annotation.tests.utils import create_test_user


class SchemaViewsTest(TestCase):

    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_site_test(self):
        response = self.client.get(reverse('site_test'))
        self.assertEqual(response.status_code, 200)

    def test_report(self):
        response = self.client.get('/site/report/')
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.client.get('/site/about/', follow=False)
        self.assertRedirects(response, status_code=301, expected_url='https://facebook.com/przypis.powszechny/',
                             fetch_redirect_response=False)

    unsubscribe_url_base = '/site/annotation_request_unsubscribe/{}/{}/'
    def test_annotation_request_unsubscribe(self):
        notification_email = 'mock@mail.com'
        annotation_request = mommy.make('annotation.AnnotationRequest')
        annotation_request.notification_email = notification_email
        annotation_request.save()

        token = Signer().sign(annotation_request.id).split(':')[1]
        response = self.client.get(self.unsubscribe_url_base.format(annotation_request.id, token))
        self.assertEqual(response.status_code, 200)
        annotation_request = AnnotationRequest.objects.get(id=annotation_request.id)
        self.assertEqual(annotation_request.notification_email, '')

    def test_annotation_request_unsubscribe_bad_token(self):
        notification_email = 'mock@mail.com'
        annotation_request = mommy.make('annotation.AnnotationRequest')
        annotation_request.notification_email = notification_email
        annotation_request.save()

        token = 'qwerty1234'
        response = self.client.get(self.unsubscribe_url_base.format(annotation_request.id, token))
        self.assertGreaterEqual(response.status_code, 400)
        annotation_request = AnnotationRequest.objects.get(id=annotation_request.id)
        self.assertEqual(annotation_request.notification_email, notification_email)

