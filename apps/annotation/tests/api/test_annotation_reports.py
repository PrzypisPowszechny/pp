import json

from django.test import TestCase
from parameterized import parameterized
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.consts import SUGGESTED_CORRECTION
from apps.annotation.models import Annotation
from apps.annotation.models import AnnotationReport
from apps.annotation.tests.utils import create_test_user


class AnnotationReportAPITest(TestCase):
    report_url = "/api/annotationReports"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token

    @parameterized.expand([
        ('SPAM', 'komentarz', 201),
        ('SPAM', '', 201),
        (SUGGESTED_CORRECTION, 'komentarz', 201),
        (SUGGESTED_CORRECTION, '', 400),

    ])
    # TODO: split this obsolete test to make it MORE UNIT
    def test_post_new_annotation_report(self, reason, comment, response_code):
        annotation = Annotation.objects.create(user=self.user)

        body = json.dumps({
            'data': {
                'type': 'annotationReports',
                'attributes': {
                    'reason': reason,
                    'comment': comment,
                },
                'relationships': {
                    'annotation': {
                        'data': {
                            'type': 'annotations',
                            'id': str(annotation.id)
                        }
                    }
                }
            }
        })

        response = self.client.post(self.report_url.format(annotation.id), body,
                                    content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, response_code, response.content)
        if 200 <= response_code < 300:
            response_data = json.loads(response.content.decode('utf8'))

            # Get first annotation report there is
            report = AnnotationReport.objects.first()
            correct_response = {
                'data': {
                    'id': str(report.id),
                    'type': 'annotationReports',
                    'attributes': {
                        'reason': reason,
                        'comment': comment,
                    },
                    'relationships': {
                        'annotation': {
                            'data': {'id': str(annotation.id), 'type': 'annotations'},
                        }
                    }
                }
            }

            self.assertEqual(response_data, correct_response)
