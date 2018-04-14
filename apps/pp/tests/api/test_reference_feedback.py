import json
from datetime import datetime, timedelta
from django.test import TestCase
from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.models import ReferenceReport
from apps.pp.tests.utils import create_test_user
from apps.pp.models import ReferenceRequest


class ReferenceFeedbackAPITest(TestCase):
    useful_url = "/api/references/{}/usefuls/"
    objection_url = "/api/references/{}/objections/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_post_useful(self):
        reference = Reference.objects.create(user=self.user)

        response = self.client.post(self.useful_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        usefuls = UserReferenceFeedback.objects.filter(user=self.user, reference=reference, useful=True).count()
        self.assertEqual(usefuls, 1)

        # Can't post second time
        response = self.client.post(self.useful_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_useful(self):
        reference = Reference.objects.create(user=self.user)

        # Can't delete when there are none
        response = self.client.delete(self.useful_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 404)

        UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True)

        response = self.client.delete(self.useful_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        usefuls = UserReferenceFeedback.objects.filter(user=self.user, reference=reference, useful=True).count()
        self.assertEqual(usefuls, 0)

    def test_post_objection(self):
        reference = Reference.objects.create(user=self.user)

        response = self.client.post(self.objection_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        objections = UserReferenceFeedback.objects.filter(user=self.user, reference=reference, objection=True).count()
        self.assertEqual(objections, 1)

        # Can't post second time
        response = self.client.post(self.objection_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_objection(self):
        reference = Reference.objects.create(user=self.user)

        # Can't delete when there are none
        response = self.client.delete(self.objection_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 404)

        UserReferenceFeedback.objects.create(user=self.user, reference=reference, objection=True)

        response = self.client.delete(self.objection_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        objections = UserReferenceFeedback.objects.filter(user=self.user, reference=reference, objection=True).count()
        self.assertEqual(objections, 0)