import json

from django.test import TestCase
from django.urls import reverse

from apps.pp.models import Annotation, AnnotationUpvote
from apps.pp.tests.utils import create_test_user


class AnnotationUpvoteAPITest(TestCase):
    upvote_url = "/api/annotation_upvotes"
    upvote_single_url = "/api/annotation_upvotes/{}"
    annotation_related_upvote_url = "/api/annotations/{}/upvote"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.get(self.upvote_single_url.format(upvote.id),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(upvote.id),
                'type': 'annotation_upvotes',
                'relationships': {
                    'annotation': {
                        'links': {
                            'related': reverse('api:annotation_upvote_related_annotation', args=(upvote.id,))
                        },
                        'data': {
                            'type': 'annotations', 'id': str(annotation.id)
                        }
                    }
                }
            }}
        )

        response = self.client.get(self.upvote_single_url.format(upvote.id + 1),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

    def test_get_annotation_related_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.get(self.annotation_related_upvote_url.format(upvote.id),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(upvote.id),
                'type': 'annotation_upvotes',
                'relationships': {
                    'annotation': {
                        'links': {
                            'related': reverse('api:annotation_upvote_related_annotation', args=(upvote.id,))
                        },
                        'data': {
                            'type': 'annotations', 'id': str(annotation.id)
                        }
                    }
                }
            }}
        )

        response = self.client.get(self.annotation_related_upvote_url.format(upvote.id + 1),
                                   content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

    def test_post_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        post_payload = {
            'data': {
                'type': 'annotation_upvote',
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
            self.upvote_url, content_type='application/vnd.api+json',
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 200)
        upvote = AnnotationUpvote.objects.last()
        self.assertIsNotNone(upvote)
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {'data': {
                'id': str(upvote.id),
                'type': 'annotation_upvotes',
                'relationships': {
                    'annotation': {
                        'links': {
                            'related': reverse('api:annotation_upvote_related_annotation', args=(upvote.id,))
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
            self.upvote_url, content_type='application/vnd.api+json',
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)

    def test_post_upvote_fail__no_relation(self):
        post_payload = {
            'data': {
                'type': 'annotation_upvote',
                'relationships': {
                    'annotation': {
                        'data': {
                            'type': 'annotation_upvote', 'id': None
                        }
                    }
                }
            }
        }

        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json',
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(AnnotationUpvote.objects.last())

        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation/data/id'
        )

        # Less and less detailed request and corresponding errors

        post_payload['data']['relationships']['annotation']['data'] = None
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json',
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation/data'
        )

        post_payload['data']['relationships']['annotation'] = None
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json',
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships/annotation'
        )

        post_payload['data']['relationships'] = None
        response = self.client.post(
            self.upvote_url, content_type='application/vnd.api+json',
            data=json.dumps(post_payload))
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(AnnotationUpvote.objects.last())
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['errors'][0]['source']['pointer'],
            '/relationships'
        )

    def test_delete_upvote(self):
        annotation = Annotation.objects.create(user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.delete(self.upvote_single_url.format(upvote.id),
                                      content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)

        upvotes = AnnotationUpvote.objects.filter(user=self.user, annotation=annotation).count()
        self.assertEqual(upvotes, 0)

        # Can't delete when there are none
        response = self.client.delete(self.upvote_single_url.format(upvote.id),
                                      content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)
