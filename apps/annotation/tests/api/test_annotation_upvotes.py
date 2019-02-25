import json

from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.annotation.models import Annotation, AnnotationUpvote
from apps.annotation.tests.utils import create_test_user, testserver_reverse


# Sqlite sometimes crashes when there are very many TestCases,
# then TransactionTestCase, which is more robust, solves the issue
class AnnotationUpvoteAPITest(TransactionTestCase):
    upvote_url = "/api/annotationUpvotes"
    upvote_single_url = "/api/annotationUpvotes/{}"
    annotation_related_upvote_url = "/api/annotations/{}/upvote"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.token = str(AccessToken.for_user(self.user))
        self.token_header = 'JWT %s' % self.token

    # TODO: split this obsolete test to make it MORE UNIT
    def test_get_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.get(self.upvote_single_url.format(upvote.id),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(upvote.id),
                'type': 'annotationUpvotes',
                'relationships': {
                    'annotation': {
                        'links': {
                            'related': testserver_reverse('api:annotation:annotation_upvote_related_annotation', args=(upvote.id,))
                        },
                        'data': {
                            'type': 'annotations', 'id': str(annotation.id)
                        }
                    }
                }
            }}
        )

        response = self.client.get(self.upvote_single_url.format(upvote.id + 1),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 404)

    # TODO: split this obsolete test to make it MORE UNIT
    def test_get_annotation_related_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.get(self.annotation_related_upvote_url.format(annotation.id),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(upvote.id),
                'type': 'annotationUpvotes',
                'relationships': {
                    'annotation': {
                        'links': {
                            'related': testserver_reverse('api:annotation:annotation_upvote_related_annotation', args=(upvote.id,))
                        },
                        'data': {
                            'type': 'annotations', 'id': str(annotation.id)
                        }
                    }
                }
            }}
        )

        response = self.client.get(self.annotation_related_upvote_url.format(annotation.id + 1),
                                   content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 404)

    # TODO: split this obsolete test to make it MORE UNIT
    # TODO: do not hardcode data all the time, use helper to create valid annotation
    def test_post_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        post_payload = {
            'data': {
                'type': 'annotationUpvotes',
                'relationships': {
                    'annotation': {
                        'data': {
                            'type': 'annotations', 'id': str(annotation.id)
                        }
                    }
                }
            }
        }

        self.assertIsNone(AnnotationUpvote.objects.last())
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 200)
        upvote = AnnotationUpvote.objects.last()
        self.assertIsNotNone(upvote)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(upvote.id),
                'type': 'annotationUpvotes',
                'relationships': {
                    'annotation': {
                        'links': {
                            'related': testserver_reverse('api:annotation:annotation_upvote_related_annotation', args=(upvote.id,))
                        },
                        'data': {
                            'type': 'annotations', 'id': str(annotation.id)
                        }
                    }
                }
            }}
        )

        # Can't post second time for the same annotation
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)

    # TODO: split this obsolete test to make it MORE UNIT
    # TODO: do not hardcode data all the time, use helper to create valid annotation
    def test_post_upvote_fail__no_relation(self):
        post_payload = {
            'data': {
                'type': 'annotationUpvotes',
                'relationships': {
                    'annotation': {
                        'data': {
                            'type': 'annotationUpvotes', 'id': None
                        }
                    }
                }
            }
        }

        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/vnd.api+json', msg=response.content.decode('utf8'))
        self.assertIsNone(AnnotationUpvote.objects.last())
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation'
        )

        # Less and less detailed request and corresponding errors

        post_payload['data']['relationships']['annotation']['data'] = None
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/vnd.api+json', msg=response.content.decode('utf8'))
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation'
        )

        post_payload['data']['relationships']['annotation'] = None
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/vnd.api+json', msg=response.content.decode('utf8'))
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation'
        )

        post_payload['data']['relationships'] = None
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(AnnotationUpvote.objects.last())
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships'
        )

    # TODO: split this obsolete test to make it MORE UNIT
    # TODO: do not hardcode data all the time, use helper to create valid annotation
    def test_post_upvote_fail__malformed_relation(self):
        post_payload = {
            'data': {
                'type': 'annotationUpvotes',
                'relationships': {
                    'annotation': {
                        'data': {
                            'type': 'annotations', 'id': None
                        }
                    }
                }
            }
        }

        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header,
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/vnd.api+json', msg=response.content.decode('utf8'))
        self.assertIsNone(AnnotationUpvote.objects.last())
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation'
        )

    # TODO: split this obsolete test to make it MORE UNIT
    def test_delete_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.delete(self.upvote_single_url.format(upvote.id),
                                      content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 200)

        upvotes = AnnotationUpvote.objects.filter(user=self.user, annotation=annotation).count()
        self.assertEqual(upvotes, 0)

        # Can't delete when there are none
        response = self.client.delete(self.upvote_single_url.format(upvote.id),
                                      content_type='application/vnd.api+json', HTTP_AUTHORIZATION=self.token_header)
        self.assertEqual(response.status_code, 404)
