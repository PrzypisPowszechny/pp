import json

from django.test import TestCase
from django.urls import reverse

from apps.pp.models import Reference
from apps.pp.models import ReferenceReport
from apps.pp.tests.utils import create_test_user


class ReferenceReportAPITest(TestCase):
    post_url = "/api/reference_reports/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_post_new_reference_report(self):
        reference = Reference.objects.create(user=self.user)

        report_data = {
            'reason': 'SPAM',
            'comment': "komentarz",
        }

        body = json.dumps({
            'data': {
                'type': 'reference_reports',
                'attributes': {
                    'reason': report_data['reason'],
                    'comment': report_data['comment'],
                },
                'relationships': {
                    'reference': {
                        'data': {
                            'type': 'reference_reports',
                            'id': str(reference.id)
                        }
                    }
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
                    'reference': {
                        'data': {'id': str(reference.id), 'type': 'references'},
                        'links': {
                            'related': reverse('api:report_reference', kwargs={'report_id': report.id})
                        }
                    }
                }
            }
        }

        self.assertEqual(response_data, correct_response)
