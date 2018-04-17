import json
from datetime import datetime, timedelta
from django.test import TestCase
from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.models import ReferenceReport
from apps.pp.tests.utils import create_test_user
from apps.pp.models import ReferenceRequest


class ReferenceReportAPITest(TestCase):
    post_url = "/api/references/{}/reports/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_post_new_reference(self):
        reference = Reference.objects.create(user=self.user)

        report_data = {
            'reason': 'SPAM',
            'comment': "komentarz",
            'reference': reference.id
        }

        body = json.dumps({
                'data': {
                    'type': 'reference_reports',
                    'attributes': {
                        'reason': report_data['reason'],
                        'comment': report_data['comment'],
                    }
                }
            })

        response = self.client.post(self.post_url.format(reference.id), body, content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf8'))

        # Get first reference report there is
        report = ReferenceReport.objects.first()
        correct_response = {
            'data': {
                'id': str(report.id),
                'type': 'reference_reports',
                'attributes': {
                    'reason': report_data['reason'],
                    'comment': report_data['comment'],
                },
                'relationships': {
                    'reference': {'data': {'id': str(reference.id), 'type': 'references'}},
                    'user': {'data': {'id': str(self.user.id), 'type': 'users'}},
                }
            }
        }

        self.assertEqual(response_data, correct_response)