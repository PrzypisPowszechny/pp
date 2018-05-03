import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_mommy import mommy
from parameterized import parameterized

from apps.pp.models import Annotation, AnnotationUpvote, AnnotationReport
from apps.pp.models import AnnotationRequest
from apps.pp.tests.utils import create_test_user
from apps.pp.utils import get_resource_name


class AnnotationAPITest(TestCase):
    base_url = "/api/annotations/{}"
    report_related_url = "/api/annotation_reports/{}/annotation"
    upvote_related_url = "/api/annotation_upvotes/{}/annotation"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_returns_json_200(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               ranges='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        response = self.client.get(self.base_url.format(annotation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_get_returns_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               ranges='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        response = self.client.get(self.base_url.format(annotation.id))

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).count()

        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(annotation.id),
                    'type': 'annotations',
                    'attributes': {
                        'url': annotation.url,
                        'ranges': json.loads(annotation.ranges),
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotation_link': annotation.annotation_link,
                        'annotation_link_title': annotation.annotation_link_title,
                        'upvote': bool(urf),
                        'upvote_count': upvote_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'upvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'id': str(urf.id), 'type': get_resource_name(urf, always_single=True)}
                        },
                        'reports': {
                            'links': {
                                'related': reverse('api:annotation_related_reports',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': []
                        },
                    }
                }
            }
        )

    def test_get_annotation_report_related_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               ranges='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        report = mommy.make(AnnotationReport, annotation=annotation, user=self.user)
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).count()

        response = self.client.get(self.report_related_url.format(report.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(annotation.id),
                    'type': 'annotations',
                    'attributes': {
                        'url': annotation.url,
                        'ranges': json.loads(annotation.ranges),
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotation_link': annotation.annotation_link,
                        'annotation_link_title': annotation.annotation_link_title,
                        'upvote': bool(urf),
                        'upvote_count': upvote_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'upvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'id': str(urf.id), 'type': get_resource_name(urf, always_single=True)}
                        },
                        'reports': {
                            'links': {
                                'related': reverse('api:annotation_related_reports',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': [
                                {'type': 'annotation_reports', 'id': str(report.id)}
                            ]
                        },
                    }
                }
            }
        )

    def test_get_annotation_upvote_related_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               ranges='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        report = mommy.make(AnnotationReport, annotation=annotation, user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).count()

        response = self.client.get(self.upvote_related_url.format(upvote.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(annotation.id),
                    'type': 'annotations',
                    'attributes': {
                        'url': annotation.url,
                        'ranges': json.loads(annotation.ranges),
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotation_link': annotation.annotation_link,
                        'annotation_link_title': annotation.annotation_link_title,
                        'upvote': bool(upvote),
                        'upvote_count': upvote_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'upvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'id': str(upvote.id), 'type': get_resource_name(upvote, always_single=True)}
                        },
                        'reports': {
                            'links': {
                                'related': reverse('api:annotation_related_reports',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': [
                                {'type': 'annotation_reports', 'id': str(report.id)}
                            ]
                        },
                    }
                }
            }
        )

    def test_empty_search_return_json_200(self):
        search_base_url = "/api/annotations?url={}"
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

        test_answer = []
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            test_answer
        )

    def test_nonempty_search_return_json_200(self):
        search_base_url = "/api/annotations?&url={}"
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               ranges='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        annotation2 = Annotation.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                                ranges='{}',
                                                annotation_link="www.przypispowszechny.com",
                                                annotation_link_title="very nice again")
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_search_return_list(self):
        search_base_url = "/api/annotations?url={}"
        # First annotation
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                               ranges='{}',
                                               url='www.przypis.pl', annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice again",
                                               create_date=timezone.now() + timedelta(seconds=-1000))
        annotation.create_date = timezone.now() + timedelta(seconds=1000)
        annotation.save()
        annotation = Annotation.objects.get(id=annotation.id)

        # Second annotation
        annotation2 = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                                ranges='{}',
                                                url='www.przypis.pl',
                                                annotation_link="www.przypispowszechny2.com",
                                                annotation_link_title="very nice",
                                                create_date=timezone.now())
        annotation2.save()

        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).count()
        upvote_count2 = AnnotationUpvote.objects.filter(annotation=annotation2).count()

        raw_response = self.client.get(search_base_url.format(annotation.url))
        response = json.loads(raw_response.content.decode('utf8'))['data']
        response_annotation = next(row for row in response if str(row['id']) == str(annotation.id))
        response_annotation2 = next(row for row in response if str(row['id']) == str(annotation2.id))
        self.assertEqual(
            response_annotation,
            {'id': str(annotation.id),
             'type': 'annotations',
             'attributes': {
                 'url': annotation.url,
                 'ranges': json.loads(annotation.ranges),
                 'quote': annotation.quote,
                 'priority': annotation.priority,
                 'comment': annotation.comment,
                 'annotation_link': annotation.annotation_link,
                 'annotation_link_title': annotation.annotation_link_title,
                 'upvote': bool(urf),
                 'upvote_count': upvote_count,
                 'does_belong_to_user': True,
             },
             'relationships': {
                 'user': {
                     'links': {
                         'related': reverse('api:annotation_related_user', kwargs={'annotation_id': annotation.id})
                     },
                     'data': {'type': 'users', 'id': str(self.user.id)}
                 },
                 'upvote': {
                     'links': {
                         'related': reverse('api:annotation_related_upvote', kwargs={'annotation_id': annotation.id})
                     },
                     'data': {'type': 'annotation_upvotes', 'id': str(urf.id)}
                 },
                 'reports': {
                     'links': {
                         'related': reverse('api:annotation_related_reports', kwargs={'annotation_id': annotation.id})
                     },
                     'data': []
                 },
             },
             'links': {
                 'self': reverse('api:annotation', kwargs={'annotation_id': annotation.id})
             }
             })

        self.assertEqual(
            response_annotation2,
            {'id': str(annotation2.id),
             'type': 'annotations',
             'attributes': {
                 'url': annotation2.url,
                 'ranges': json.loads(annotation2.ranges),
                 'quote': annotation2.quote,
                 'priority': annotation2.priority,
                 'comment': annotation2.comment,
                 'annotation_link': annotation2.annotation_link,
                 'annotation_link_title': annotation2.annotation_link_title,
                 'upvote': False,
                 'upvote_count': upvote_count2,
                 'does_belong_to_user': True,
             },
             'relationships': {
                 'user': {
                     'links': {
                         'related': reverse('api:annotation_related_user', kwargs={'annotation_id': annotation2.id})
                     },
                     'data': {'type': 'users', 'id': str(self.user.id)}
                 },
                 'upvote': {
                     'links': {
                         'related': reverse('api:annotation_related_upvote', kwargs={'annotation_id': annotation2.id})
                     },
                     'data': None
                 },
                 'reports': {
                     'links': {
                         'related': reverse('api:annotation_related_reports', kwargs={'annotation_id': annotation2.id})
                     },
                     'data': []
                 },
             },
             'links': {
                 'self': reverse('api:annotation', kwargs={'annotation_id': annotation2.id})
             },
             })

    @parameterized.expand([
        [{'start': "Od tad", 'end': "do tad"}],
        [{}],
        ['string range: od tad do tad'],
        [''],
    ])
    def test_post_new_annotation(self, ranges):
        base_url = "/api/annotations"
        response = self.client.post(
            base_url,
            json.dumps({
                'data': {
                    'type': 'annotations',
                    'attributes': {
                        'url': "www.przypis.pl",
                        'ranges': ranges,
                        'quote': 'very nice',
                        'priority': 'NORMAL',
                        'comment': "komentarz",
                        'annotation_link': 'www.przypispowszechny.com',
                        'annotation_link_title': 'very nice too',
                    },
                }
            }),
            content_type='application/vnd.api+json')

        self.assertEqual(response.status_code, 200, msg=response.data)
        annotation = Annotation.objects.get(user=self.user)

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).count()

        # Check response
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(annotation.id),
                    'type': 'annotations',
                    'attributes': {
                        'url': annotation.url,
                        'ranges': ranges,
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotation_link': annotation.annotation_link,
                        'annotation_link_title': annotation.annotation_link_title,
                        'upvote': False,
                        'upvote_count': upvote_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'upvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': None
                        },
                        'reports': {
                            'links': {
                                'related': reverse('api:annotation_related_reports',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': []
                        },
                    }
                }
            }
        )

        # Check if ranges is stored as json (despite being posted and returned as normal dict)
        self.assertEqual(annotation.ranges, json.dumps(ranges))

    def test_patch_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', url='www.przypis.pl',
                                               comment="good job",
                                               ranges='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice",
                                               quote='not this time')
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        put_string = 'not so well'
        put_data = json.dumps({
            'data': {
                'id': annotation.id,
                'type': 'annotations',
                'attributes': {
                    'annotation_link_title': put_string
                }
            }
        })
        response = self.client.patch(self.base_url.format(annotation.id), put_data,
                                     content_type='application/vnd.api+json')
        annotation = Annotation.objects.get(id=annotation.id)

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(annotation.annotation_link_title, put_string)
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            {
                'id': str(annotation.id),
                'type': 'annotations',
                'attributes': {
                    'url': annotation.url,
                    'ranges': json.loads(annotation.ranges),
                    'quote': annotation.quote,
                    'priority': annotation.priority,
                    'comment': annotation.comment,
                    'annotation_link': annotation.annotation_link,
                    'annotation_link_title': annotation.annotation_link_title,
                    'upvote': bool(urf),
                    'upvote_count': upvote_count,
                    'does_belong_to_user': True,
                },
                'relationships': {
                    'user': {
                        'links': {
                            'related': reverse('api:annotation_related_user', kwargs={'annotation_id': annotation.id})
                        },
                        'data': {'type': 'users', 'id': str(self.user.id)}
                    },
                    'upvote': {
                        'links': {
                            'related': reverse('api:annotation_related_upvote', kwargs={'annotation_id': annotation.id})
                        },
                        'data': {'id': str(urf.id), 'type': get_resource_name(urf, always_single=True)}
                    },
                    'reports': {
                        'links': {
                            'related': reverse('api:annotation_related_reports',
                                               kwargs={'annotation_id': annotation.id})
                        },
                        'data': []
                    },
                }
            }

        )

    def test_patch_inaccessible_field_annotation(self):
        annotation = Annotation.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            ranges='{}',
            annotation_link="www.przypispowszechny.com", annotation_link_title="very nice",
            quote='not this time'
        )
        AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        put_string = 'not so well'
        put_data = json.dumps({
            'data': {
                'type': 'annotations',
                'id': annotation.id,
                'attributes': {
                    'quote': put_string
                }
            }
        })
        response = self.client.patch(self.base_url.format(annotation.id), put_data,
                                     content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 400)

    def test_patch_inaccessible_relationhips_annotation(self):
        annotation = Annotation.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            ranges='{}',
            annotation_link="www.przypispowszechny.com", annotation_link_title="very nice",
            quote='not this time'
        )
        AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        put_string = 'not so well'
        put_data = json.dumps({
            'data': {
                'type': 'annotations',
                'id': annotation.id,
                'attributes': {
                    'annotation_link_title': put_string
                },
                'relationships': {}
            }
        })
        response = self.client.patch(self.base_url.format(annotation.id), put_data,
                                     content_type='application/vnd.api+json')
        annotation = Annotation.objects.get(id=annotation.id)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(annotation.comment, put_string)

    def test_patch_deny_non_owner(self):
        owner_user, owner_user_pass = create_test_user(unique=True)
        annotation = Annotation.objects.create(
            user=owner_user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            annotation_link="www.przypispowszechny.com", annotation_link_title="very nice",
            quote='not this time'
        )
        put_string = 'not so well'
        put_data = json.dumps({
            'data': {
                'type': 'annotations',
                'id': annotation.id,
                'attributes': {
                    'annotation_link_title': put_string
                }
            }
        })
        response = self.client.patch(self.base_url.format(annotation.id), put_data,
                                     content_type='application/vnd.api+json')
        annotation = Annotation.objects.get(id=annotation.id)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(annotation.comment, put_string)

    def test_delete_annotation(self):
        annotation = Annotation.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            annotation_link="www.przypispowszechny.com", annotation_link_title="very nice",
            quote='not this time'
        )
        AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        good_id = annotation.id
        non_existing_id = good_id + 100000000

        response = self.client.delete(self.base_url.format(good_id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)

        # After removing is not accessible
        response = self.client.get(self.base_url.format(good_id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)

        # Removing again is still good
        response = self.client.delete(self.base_url.format(good_id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200)

        # Removing never existing is bad
        response = self.client.delete(self.base_url.format(non_existing_id), content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 404)
