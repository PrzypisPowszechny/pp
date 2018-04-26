from django.test import TestCase

from apps.pp.models import Reference, ReferenceUpvote
from apps.pp.tests.utils import create_test_user


class ReferenceFeedbackAPITest(TestCase):
    upvote_url = "/api/references/{}/upvote/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_post_upvote(self):
        reference = Reference.objects.create(user=self.user)

        response = self.client.post(self.upvote_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        upvotes = ReferenceUpvote.objects.filter(user=self.user, reference=reference).count()
        self.assertEqual(upvotes, 1)

        # Can't post second time
        response = self.client.post(self.upvote_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 400)

    def test_delete_upvote(self):
        reference = Reference.objects.create(user=self.user)

        # Can't delete when there are none
        response = self.client.delete(self.upvote_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

        ReferenceUpvote.objects.create(user=self.user, reference=reference)

        response = self.client.delete(self.upvote_url.format(reference.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        upvotes = ReferenceUpvote.objects.filter(user=self.user, reference=reference).count()
        self.assertEqual(upvotes, 0)
