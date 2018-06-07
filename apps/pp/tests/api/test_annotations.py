import json
from datetime import timedelta
from urllib.parse import quote

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_mommy import mommy
from parameterized import parameterized
from rest_framework import serializers

from apps.pp.models import Annotation, AnnotationUpvote, AnnotationReport
from apps.pp.tests.utils import create_test_user
from apps.pp.utils import get_resource_name


class AnnotationAPITest(TestCase):
    base_url = "/api/annotations/{}"
    report_related_url = "/api/annotationReports/{}/annotation"
    upvote_related_url = "/api/annotationUpvotes/{}/annotation"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_returns_json_200(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               range='{}',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        response = self.client.get(self.base_url.format(annotation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_get_returns_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               range='{}', url='http://localhost/',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        response = self.client.get(self.base_url.format(annotation.id))

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(annotation.id),
                    'type': 'annotations',
                    'attributes': {
                        'url': annotation.url,
                        'range': json.loads(annotation.range),
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotationLink': annotation.annotation_link,
                        'annotationLinkTitle': annotation.annotation_link_title,
                        'createDate': serializers.DateTimeField().to_representation(annotation.create_date),
                        'upvoteCountExceptUser': upvote_count,
                        'doesBelongToUser': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'annotationUpvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
                        },
                        'annotationReports': {
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

    def test_get_returns_annotation__upvote_count(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               range='{}', url='http://localhost/',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")

        # No relation, no count

        response = self.client.get(self.base_url.format(annotation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertIsNotNone(response_content_data)
        attributes = response_content_data.get('attributes')
        self.assertIsNotNone(attributes)
        self.assertEqual(attributes.get('upvoteCountExceptUser'), 0)
        relationships = response_content_data.get('relationships')
        self.assertIsNotNone(relationships)
        self.assertDictEqual(relationships.get('annotationUpvote'), {
            'links': {
                'related': reverse('api:annotation_related_upvote',
                                   kwargs={'annotation_id': annotation.id})
            },
            'data': None
        })

        # Existing relation, no count

        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.get(self.base_url.format(annotation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertIsNotNone(response_content_data)
        attributes = response_content_data.get('attributes')
        self.assertIsNotNone(attributes)
        self.assertEqual(attributes.get('upvoteCountExceptUser'), 0)
        relationships = response_content_data.get('relationships')
        self.assertIsNotNone(relationships)
        self.assertDictEqual(relationships.get('annotationUpvote'), {
            'links': {
                'related': reverse('api:annotation_related_upvote',
                                   kwargs={'annotation_id': annotation.id})
            },
            'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
        })

        # Existing relation, positive count

        other_user1, password1 = create_test_user(unique=True)
        other_user2, password2 = create_test_user(unique=True)
        AnnotationUpvote.objects.create(user=other_user1, annotation=annotation)
        AnnotationUpvote.objects.create(user=other_user2, annotation=annotation)
        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

        response = self.client.get(self.base_url.format(annotation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertIsNotNone(response_content_data)
        attributes = response_content_data.get('attributes')
        self.assertIsNotNone(attributes)
        self.assertEqual(attributes.get('upvoteCountExceptUser'), upvote_count)
        relationships = response_content_data.get('relationships')
        self.assertIsNotNone(relationships)
        self.assertDictEqual(relationships.get('annotationUpvote'), {
            'links': {
                'related': reverse('api:annotation_related_upvote',
                                   kwargs={'annotation_id': annotation.id})
            },
            'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
        })

    def test_get_annotation_report_related_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               range='{}', url='http://localhost/',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        report = mommy.make(AnnotationReport, annotation=annotation, user=self.user)
        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

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
                        'range': json.loads(annotation.range),
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotationLink': annotation.annotation_link,
                        'annotationLinkTitle': annotation.annotation_link_title,
                        'createDate': serializers.DateTimeField().to_representation(annotation.create_date),
                        'upvoteCountExceptUser': upvote_count,
                        'doesBelongToUser': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'annotationUpvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
                        },
                        'annotationReports': {
                            'links': {
                                'related': reverse('api:annotation_related_reports',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': [
                                {'type': 'annotationReports', 'id': str(report.id)}
                            ]
                        },
                    }
                }
            }
        )

    def test_get_annotation_upvote_related_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               range='{}', url='http://localhost/',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")
        report = mommy.make(AnnotationReport, annotation=annotation, user=self.user)
        upvote = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)
        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

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
                        'range': json.loads(annotation.range),
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotationLink': annotation.annotation_link,
                        'annotationLinkTitle': annotation.annotation_link_title,
                        'createDate': serializers.DateTimeField().to_representation(annotation.create_date),
                        'upvoteCountExceptUser': upvote_count,
                        'doesBelongToUser': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'annotationUpvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'id': str(upvote.id), 'type': 'annotationUpvotes'}
                        },
                        'annotationReports': {
                            'links': {
                                'related': reverse('api:annotation_related_reports',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': [
                                {'type': 'annotationReports', 'id': str(report.id)}
                            ]
                        },
                    }
                }
            }
        )

    def test_list_annotations_empty_return_json_200(self):
        search_base_url = "/api/annotations?url={}"
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

        test_answer = []
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            test_answer
        )

    def test_list_annotations__nonempty_return_json_200(self):
        annotation_url = 'http://example.com/subpage.html'
        search_base_url = "/api/annotations"
        Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                  range='{}', url=annotation_url,
                                  annotation_link="www.przypispowszechny.com",
                                  annotation_link_title="very nice")
        Annotation.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                  range='{}', url=annotation_url,
                                  annotation_link="www.przypispowszechny.com",
                                  annotation_link_title="very nice again")

        response = self.client.get(search_base_url.format(annotation_url))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertIsNotNone(response_content_data)
        self.assertEqual(len(response_content_data), 2)

    @parameterized.expand([
        # No filtering - include
        ("https://docs.python.org/",
         "",
         1),
        # Exact - include
        ("https://docs.python.org/",
         "https://docs.python.org/",
         1),
        # Protocol different - include
        ("https://docs.python.org/",
         "http://docs.python.org/",
         1),
        # Domain different - exclude
        ("https://docs.python.org/",
         "https://docs.python.com/",
         0),
        # Slash different - include
        ("https://docs.python.org",
         "https://docs.python.org/",
         1),
        # Slash different - include
        ("https://docs.python.org/",
         "https://docs.python.org",
         1),
        # Path different - exclude
        ("https://docs.python.org/",
         "https://docs.python.org/page",
         0),
        # Fragment (anchor) different - include
        ("https://docs.python.org/2/library/urlparse.html?a=1&b=2#urlparse-result-object",
         "https://docs.python.org/2/library/urlparse.html?a=1&b=2#differnt-anchor",
         1),
        # Fragment (anchor) different - include
        ("https://docs.python.org/2/library/urlparse.html?",
         "https://docs.python.org/2/library/urlparse.html",
         1),
        # Irrelevant querystring different - include
        ("https://docs.python.org/2/library/urlparse.html?utm_campaign=buy-it&a=1",
         "https://docs.python.org/2/library/urlparse.html?a=1",
         1),
        # Relevant querystring different - exclude
        ("https://docs.python.org/2/library/urlparse.html?a=black",
         "https://docs.python.org/2/library/urlparse.html?a=white",
         0),
    ])
    def test_list_annotations__url_filtering(self, annotation_url, query_url, expected_count):
        search_base_url = "/api/annotations?&url={}"
        Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                  range='{}', url=annotation_url,
                                  annotation_link="www.przypispowszechny.com",
                                  annotation_link_title="very nice")
        response = self.client.get(search_base_url.format(quote(query_url)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertIsNotNone(response_content_data)
        self.assertEqual(len(response_content_data), expected_count)

    def test_list_annotations__exact_records(self):
        search_base_url = "/api/annotations?url={}"
        # First annotation
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                               range='{}',
                                               url='www.przypis.pl', annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice again",
                                               create_date=timezone.now() + timedelta(seconds=-1000))
        annotation.create_date = timezone.now() + timedelta(seconds=1000)
        annotation.save()
        annotation = Annotation.objects.get(id=annotation.id)

        # Second annotation
        annotation2 = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                                range='{}',
                                                url='www.przypis.pl',
                                                annotation_link="www.przypispowszechny2.com",
                                                annotation_link_title="very nice",
                                                create_date=timezone.now())
        annotation2.save()

        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()
        upvote_count2 = AnnotationUpvote.objects.filter(annotation=annotation2).exclude(user=self.user).count()

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
                 'range': json.loads(annotation.range),
                 'quote': annotation.quote,
                 'priority': annotation.priority,
                 'comment': annotation.comment,
                 'annotationLink': annotation.annotation_link,
                 'annotationLinkTitle': annotation.annotation_link_title,
                 'createDate': serializers.DateTimeField().to_representation(annotation.create_date),
                 'upvoteCountExceptUser': upvote_count,
                 'doesBelongToUser': True,
             },
             'relationships': {
                 'user': {
                     'links': {
                         'related': reverse('api:annotation_related_user', kwargs={'annotation_id': annotation.id})
                     },
                     'data': {'type': 'users', 'id': str(self.user.id)}
                 },
                 'annotationUpvote': {
                     'links': {
                         'related': reverse('api:annotation_related_upvote', kwargs={'annotation_id': annotation.id})
                     },
                     'data': {'type': 'annotationUpvotes', 'id': str(urf.id)}
                 },
                 'annotationReports': {
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
                 'range': json.loads(annotation2.range),
                 'quote': annotation2.quote,
                 'priority': annotation2.priority,
                 'comment': annotation2.comment,
                 'annotationLink': annotation2.annotation_link,
                 'annotationLinkTitle': annotation2.annotation_link_title,
                 'createDate': serializers.DateTimeField().to_representation(annotation2.create_date),
                 'upvoteCountExceptUser': upvote_count2,
                 'doesBelongToUser': True,
             },
             'relationships': {
                 'user': {
                     'links': {
                         'related': reverse('api:annotation_related_user', kwargs={'annotation_id': annotation2.id})
                     },
                     'data': {'type': 'users', 'id': str(self.user.id)}
                 },
                 'annotationUpvote': {
                     'links': {
                         'related': reverse('api:annotation_related_upvote', kwargs={'annotation_id': annotation2.id})
                     },
                     'data': None
                 },
                 'annotationReports': {
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

    def test_list_annotations__upvote_count(self):
        list_url = '/api/annotations'
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                               range='{}', url='http://localhost/',
                                               annotation_link="www.przypispowszechny.com",
                                               annotation_link_title="very nice")

        # No relation, no count

        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertTrue(response_content_data)
        attributes = response_content_data[0].get('attributes')
        self.assertIsNotNone(attributes)
        self.assertEqual(attributes.get('upvoteCountExceptUser'), 0)
        relationships = response_content_data[0].get('relationships')
        self.assertIsNotNone(relationships)
        self.assertDictEqual(relationships.get('annotationUpvote'), {
            'links': {
                'related': reverse('api:annotation_related_upvote',
                                   kwargs={'annotation_id': annotation.id})
            },
            'data': None
        })

        # Existing relation, no count

        urf = AnnotationUpvote.objects.create(user=self.user, annotation=annotation)

        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertTrue(response_content_data)
        attributes = response_content_data[0].get('attributes')
        self.assertIsNotNone(attributes)
        self.assertEqual(attributes.get('upvoteCountExceptUser'), 0)
        relationships = response_content_data[0].get('relationships')
        self.assertIsNotNone(relationships)
        self.assertDictEqual(relationships.get('annotationUpvote'), {
            'links': {
                'related': reverse('api:annotation_related_upvote',
                                   kwargs={'annotation_id': annotation.id})
            },
            'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
        })

        # Existing relation, positive count

        other_user1, password1 = create_test_user(unique=True)
        other_user2, password2 = create_test_user(unique=True)
        AnnotationUpvote.objects.create(user=other_user1, annotation=annotation)
        AnnotationUpvote.objects.create(user=other_user2, annotation=annotation)
        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')
        response_content_data = json.loads(response.content.decode('utf8')).get('data')
        self.assertTrue(response_content_data)
        attributes = response_content_data[0].get('attributes')
        self.assertIsNotNone(attributes)
        self.assertEqual(attributes.get('upvoteCountExceptUser'), upvote_count)
        relationships = response_content_data[0].get('relationships')
        self.assertIsNotNone(relationships)
        self.assertDictEqual(relationships.get('annotationUpvote'), {
            'links': {
                'related': reverse('api:annotation_related_upvote',
                                   kwargs={'annotation_id': annotation.id})
            },
            'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
        })

    def get_valid_request_template(self):
        return {
            'data': {
                'type': 'annotations',
                'attributes': {
                    'url': "http://www.przypis.pl/",
                    'range': {'start': "Od tad", 'end': "do tad"},
                    'quote': 'very nice',
                    'priority': 'NORMAL',
                    'comment': "komentarz",
                    'annotationLink': 'www.przypispowszechny.com',
                    'annotationLinkTitle': 'very nice too',
                },
            }
        }

    def test_post_new_annotation__exact(self):
        base_url = "/api/annotations"
        request_payload = self.get_valid_request_template()
        response = self.client.post(
            base_url,
            json.dumps(request_payload),
            content_type='application/vnd.api+json')

        self.assertEqual(response.status_code, 200, msg=response.data)
        annotation = Annotation.objects.get(user=self.user)

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

        # Check response
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(annotation.id),
                    'type': 'annotations',
                    'attributes': {
                        'url': annotation.url,
                        'range': request_payload['data']['attributes']['range'],
                        'quote': annotation.quote,
                        'priority': annotation.priority,
                        'comment': annotation.comment,
                        'annotationLink': annotation.annotation_link,
                        'annotationLinkTitle': annotation.annotation_link_title,
                        'createDate': serializers.DateTimeField().to_representation(annotation.create_date),
                        'upvoteCountExceptUser': upvote_count,
                        'doesBelongToUser': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:annotation_related_user',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'annotationUpvote': {
                            'links': {
                                'related': reverse('api:annotation_related_upvote',
                                                   kwargs={'annotation_id': annotation.id})
                            },
                            'data': None
                        },
                        'annotationReports': {
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

    @parameterized.expand([
        [{'start': "Od tad", 'end': "do tad"}],
        [{}],
        ['string range: od tad do tad'],
        [''],
    ])
    def test_post_and_patch_annotation__field_range(self, range):
        # POST
        base_url = "/api/annotations"
        request_payload = self.get_valid_request_template()
        request_payload['data']['attributes']['range'] = range
        response = self.client.post(
            base_url,
            json.dumps(request_payload),
            content_type='application/vnd.api+json')

        self.assertEqual(response.status_code, 200, msg=response.data)
        new_annotation = Annotation.objects.filter(user=self.user).last()
        self.assertIsNotNone(new_annotation)
        self.assertEqual(response['content-type'], 'application/vnd.api+json', msg=response.content.decode('utf8'))
        response_data = json.loads(response.content.decode('utf8'))
        self.assertEqual(
            response_data['data']['attributes']['range'], range
        )

        # Check if range is stored as json (despite being posted and returned as normal dict)
        self.assertEqual(new_annotation.range, json.dumps(range))

        # PATCH
        id = response_data['data']['id']
        response = self.client.patch(
            '{}/{}'.format(base_url, id),
            json.dumps(request_payload),
            content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200, msg=response.data)
        response_data = json.loads(response.content.decode('utf8'))
        self.assertEqual(
            response_data['data']['attributes']['range'], range
        )


    @parameterized.expand([
        ['komentarz'],
        [''],
        [None],
    ])
    def test_post_and_patch_annotation__field_comment(self, comment):
        # POST
        base_url = "/api/annotations"
        request_payload = self.get_valid_request_template()
        if comment is not None:
            request_payload['data']['attributes']['comment'] = comment
        else:
            request_payload['data']['attributes'].pop('comment')
        response = self.client.post(
            base_url,
            json.dumps(request_payload),
            content_type='application/vnd.api+json')
        response_data = json.loads(response.content.decode('utf8'))

        self.assertEqual(response.status_code, 200, msg=response.data)
        new_annotation = Annotation.objects.filter(user=self.user).last()
        self.assertIsNotNone(new_annotation)
        self.assertEqual(response['content-type'], 'application/vnd.api+json', msg=response.content.decode('utf8'))
        self.assertEqual(
            response_data['data']['attributes']['comment'], comment or ""
        )

        # PATCH
        id = response_data['data']['id']
        response = self.client.patch(
            '{}/{}'.format(base_url, id),
            json.dumps(request_payload),
            content_type='application/vnd.api+json')
        self.assertEqual(response.status_code, 200, msg=response.data)
        self.assertEqual(
            response_data['data']['attributes']['comment'], comment or ""
        )

    def test_patch_annotation(self):
        annotation = Annotation.objects.create(user=self.user, priority='NORMAL', url='www.przypis.pl',
                                               comment="good job",
                                               range='{}',
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
                    'annotationLinkTitle': put_string
                }
            }
        })
        response = self.client.patch(self.base_url.format(annotation.id), put_data,
                                     content_type='application/vnd.api+json')
        annotation = Annotation.objects.get(id=annotation.id)

        upvote_count = AnnotationUpvote.objects.filter(annotation=annotation).exclude(user=self.user).count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(annotation.annotation_link_title, put_string)
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            {
                'id': str(annotation.id),
                'type': 'annotations',
                'attributes': {
                    'url': annotation.url,
                    'range': json.loads(annotation.range),
                    'quote': annotation.quote,
                    'priority': annotation.priority,
                    'comment': annotation.comment,
                    'annotationLink': annotation.annotation_link,
                    'annotationLinkTitle': annotation.annotation_link_title,
                    'createDate': serializers.DateTimeField().to_representation(annotation.create_date),
                    'upvoteCountExceptUser': upvote_count,
                    'doesBelongToUser': True,
                },
                'relationships': {
                    'user': {
                        'links': {
                            'related': reverse('api:annotation_related_user', kwargs={'annotation_id': annotation.id})
                        },
                        'data': {'type': 'users', 'id': str(self.user.id)}
                    },
                    'annotationUpvote': {
                        'links': {
                            'related': reverse('api:annotation_related_upvote', kwargs={'annotation_id': annotation.id})
                        },
                        'data': {'id': str(urf.id), 'type': 'annotationUpvotes'}
                    },
                    'annotationReports': {
                        'links': {
                            'related': reverse('api:annotation_related_reports',
                                               kwargs={'annotation_id': annotation.id})
                        },
                        'data': []
                    },
                }
            }

        )

    def test_patch_annotation__deny__attribute_quote(self):
        annotation = Annotation.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            range='{}',
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

    def test_patch_annotation__deny__relationship_annotation(self):
        annotation = Annotation.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            range='{}',
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
                    'annotationLinkTitle': put_string
                },
                'relationships': {}
            }
        })
        response = self.client.patch(self.base_url.format(annotation.id), put_data,
                                     content_type='application/vnd.api+json')
        annotation = Annotation.objects.get(id=annotation.id)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(annotation.comment, put_string)

    def test_patch_annotation__deny__non_owner(self):
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
                    'annotationLinkTitle': put_string
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
