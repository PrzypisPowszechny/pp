import json

from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from apps.pp.models import Annotation
from apps.pp.models import AnnotationReport
from apps.pp.tests.utils import create_test_user


class AnnotationReportAPITest(TestCase):
    report_url = "/api/annotation_reports/"
    report_single_url = "/api/annotation_reports/{}/"
    annotation_related_reports_url = "/api/annotations/{}/reports/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_annotation_report(self):
        annotation = Annotation.objects.create(user=self.user)
        report = mommy.make(AnnotationReport, annotation=annotation, user=self.user)
        response = self.client.get(self.report_single_url.format(report.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(report.id),
                'type': 'annotation_reports',
                'attributes': {
                    'reason': report.reason,
                    'comment': report.comment,
                },
                'relationships': {
                    'annotation': {
                        'data': {'id': str(annotation.id), 'type': 'annotations'},
                        'links': {
                            'related': reverse('api:annotation_report_related_annotation',
                                               kwargs={'report_id': report.id})
                        }
                    }
                }
            }}
        )

        response = self.client.get(self.report_single_url.format(report.id + 1),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

    def test_get_annotation_report__deny_other_user(self):
        owner_user, owner_user_password = create_test_user(unique=True)
        annotation = Annotation.objects.create(user=owner_user)
        report = mommy.make(AnnotationReport, annotation=annotation, user=owner_user)
        response = self.client.get(self.report_single_url.format(report.id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

    def test_get_annotation_related_annotation_report(self):
        annotation = Annotation.objects.create(user=self.user)
        report = mommy.make(AnnotationReport, annotation=annotation, user=self.user)
        response = self.client.get(self.annotation_related_reports_url.format(annotation.id),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data':
                [{
                    'id': str(report.id),
                    'type': 'annotation_reports',
                    'attributes': {
                        'reason': report.reason,
                        'comment': report.comment,
                    },
                    'relationships': {
                        'annotation': {
                            'data': {'id': str(annotation.id), 'type': 'annotations'},
                            'links': {
                                'related': reverse('api:annotation_report_related_annotation',
                                                   kwargs={'report_id': report.id})
                            }
                        }
                    }
                }]
            }
        )

        response = self.client.get(self.report_single_url.format(report.id + 1),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)


    def test_post_new_annotation_report(self):
        annotation = Annotation.objects.create(user=self.user)

        report_data = {
            'reason': 'SPAM',
            'comment': "komentarz",
        }

        body = json.dumps({
            'data': {
                'type': 'annotation_reports',
                'attributes': {
                    'reason': report_data['reason'],
                    'comment': report_data['comment'],
                },
                'relationships': {
                    'annotation': {
                        'data': {
                            'type': 'annotation_reports',
                            'id': str(annotation.id)
                        }
                    }
                }
            }
        })

        response = self.client.post(self.report_url.format(annotation.id), body, content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf8'))

        # Get first annotation report there is
        report = AnnotationReport.objects.first()
        correct_response = {
            'data': {
                'id': str(report.id),
                'type': 'annotation_reports',
                'attributes': {
                    'reason': report_data['reason'],
                    'comment': report_data['comment'],
                },
                'relationships': {
                    'annotation': {
                        'data': {'id': str(annotation.id), 'type': 'annotations'},
                        'links': {
                            'related': reverse('api:annotation_report_related_annotation',
                                               kwargs={'report_id': report.id})
                        }
                    }
                }
            }
        }

        self.assertEqual(response_data, correct_response)
