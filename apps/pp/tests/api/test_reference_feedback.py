from django.test import TestCase

from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.tests.utils import create_test_user


class ReferenceFeedbackAPITest(TestCase):
    useful_url = "/api/references/{}/useful/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_post_useful(self):
        reference = Reference.objects.create(user=self.user)

        response = self.client.post(self.useful_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        usefuls = UserReferenceFeedback.objects.filter(user=self.user, reference=reference).count()
        self.assertEqual(usefuls, 1)

        # Can't post second time
        response = self.client.post(self.useful_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 400)

    def test_delete_useful(self):
        reference = Reference.objects.create(user=self.user)

        # Can't delete when there are none
        response = self.client.delete(self.useful_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

        UserReferenceFeedback.objects.create(user=self.user, reference=reference)

        response = self.client.delete(self.useful_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        usefuls = UserReferenceFeedback.objects.filter(user=self.user, reference=reference).count()
        self.assertEqual(usefuls, 0)
