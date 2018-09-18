import json

from django.test import TestCase

from apps.annotation.models import Annotation
from apps.annotation.tests.utils import create_test_user


class LazySignupAnnotationAPITest(TestCase):
    GET_base_url = "/api/annotations/{}"
    POST_url = "/api/annotations"

    def test_client_can_access_annotation(self):
        self.user, self.password = create_test_user()

        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        response = self.client.get(self.GET_base_url.format(annotation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_client_can_post_annotation(self):
        response = self.client.post(
            self.POST_url,
            json.dumps({
                'data': {
                    'type': 'annotations',
                    'attributes': {
                        'url': "https://www.przypis.pl",
                        'range': "Od tad do tad",
                        'quote': 'very nice',
                        'priority': 'NORMAL',
                        'ppCategory': Annotation.ADDITIONAL_INFO,
                        'comment': "komentarz",
                        'annotationLink': 'www.przypispowszechny.com',
                        'annotationLinkTitle': 'very nice too'
                    }
                }
            }),
            content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200, 'Full Response: \n%s' % response.content.decode('utf8'))

    # Even if the user doesn't log, two annotations posted by the same client should have
    # Within the first one, a User is created
    # Within the second one, it is recognised based on session cookies
    def test_client_maintains_identity_across_requests(self):
        annotation_json = json.dumps({
            'data': {
                'type': 'annotations',
                'attributes': {
                    'url': "http://www.przypis.pl",
                    'range': "Od tad do tad",
                    'quote': 'very nice',
                    'priority': 'NORMAL',
                    'ppCategory': Annotation.ADDITIONAL_INFO,
                    'comment': "komentarz",
                    'annotationLink': 'www.przypispowszechny.com',
                    'annotationLinkTitle': 'very nice too'
                }
            }
        })

        # Post two annotations
        response = self.client.post(
            self.POST_url,
            annotation_json,
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200, 'Full Response: \n%s' % response.content.decode('utf8'))
        annotation_id = json.loads(response.content.decode('utf8'))['data']['id']

        response = self.client.post(
            self.POST_url,
            annotation_json,
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        annotation_id2 = json.loads(response.content.decode('utf8'))['data']['id']

        annotation = Annotation.objects.get(id=annotation_id)
        annotation2 = Annotation.objects.get(id=annotation_id2)
        self.assertEqual(annotation.user.id, annotation2.user.id)
