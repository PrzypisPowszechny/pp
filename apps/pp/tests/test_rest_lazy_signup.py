import json

from django.test import TestCase

from apps.pp.models import Reference
from apps.pp.tests.utils import create_test_user


class LazySignupReferenceAPITest(TestCase):
    GET_base_url = "/api/references/{}/"
    POST_url = "/api/references/"

    def test_client_can_access_reference(self):
        self.user, self.password = create_test_user()

        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        response = self.client.get(self.GET_base_url.format(reference.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_client_can_post_reference(self):
        response = self.client.post(
            self.POST_url,
            json.dumps({
                'data': {
                    'type': 'references',
                    'attributes': {
                        'url': "www.przypis.pl",
                        'ranges': "Od tad do tad",
                        'quote': 'very nice',
                        'priority': 'NORMAL',
                        'comment': "komentarz",
                        'link': 'www.przypispowszechny.com',
                        'link_title': 'very nice too'
                    }
                }
            }),
            content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)

    # Even if the user doesn't log, two references posted by the same client should have
    # Within the first one, a User is created
    # Within the second one, it is recognised based on session cookies
    def test_client_maintains_identity_across_requests(self):
        reference_json = json.dumps({
                'data': {
                    'type': 'references',
                    'attributes': {
                        'url': "www.przypis.pl",
                        'ranges': "Od tad do tad",
                        'quote': 'very nice',
                        'priority': 'NORMAL',
                        'comment': "komentarz",
                        'link': 'www.przypispowszechny.com',
                        'link_title': 'very nice too'
                    }
                }
            })

        # Post two references
        response = self.client.post(
            self.POST_url,
            reference_json,
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        reference_id = json.loads(response.content.decode('utf8'))['data']['id']

        response = self.client.post(
            self.POST_url,
            reference_json,
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200)
        reference_id2 = json.loads(response.content.decode('utf8'))['data']['id']


        reference = Reference.objects.get(id=reference_id)
        reference2 = Reference.objects.get(id=reference_id2)
        self.assertEqual(reference.user.id, reference2.user.id)