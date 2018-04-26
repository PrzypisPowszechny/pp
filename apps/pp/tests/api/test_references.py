import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.models import ReferenceRequest
from apps.pp.tests.utils import create_test_user
from apps.pp.utils import get_resource_name


class ReferenceAPITest(TestCase):
    base_url = "/api/references/{}/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_returns_json_200(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             reference_link="www.przypispowszechny.com",
                                             reference_link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference)
        response = self.client.get(self.base_url.format(reference.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_get_returns_reference(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             reference_link="www.przypispowszechny.com",
                                             reference_link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference)
        response = self.client.get(self.base_url.format(reference.id))

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).count()

        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(reference.id),
                    'type': 'references',
                    'attributes': {
                        'url': reference.url,
                        'ranges': reference.ranges,
                        'quote': reference.quote,
                        'priority': reference.priority,
                        'comment': reference.comment,
                        'reference_link': reference.reference_link,
                        'reference_link_title': reference.reference_link_title,
                        'useful': bool(urf),
                        'useful_count': useful_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                            'links': {
                                'related': reverse('api:reference_user', kwargs={'reference_id': reference.id})
                            },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'useful': {
                            'links': {
                                'related': reverse('api:reference_useful', kwargs={'reference_id': reference.id})
                            },
                            'data': {'id': str(urf.id), 'type': get_resource_name(urf, always_single=True)}
                        },
                        'reference_reports': {
                            'links': {
                                'related': reverse('api:reference_reports', kwargs={'reference_id': reference.id})
                            },
                            'data': []
                        },
                    }
                }
            }
        )

    def test_empty_search_return_json_200(self):
        search_base_url = "/api/references/?url={}"
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

        test_answer = []
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            test_answer
        )

    def test_nonempty_search_return_json_200(self):
        search_base_url = "/api/references/?&url={}"
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             reference_link="www.przypispowszechny.com",
                                             reference_link_title="very nice")
        reference2 = Reference.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                              reference_link="www.przypispowszechny.com",
                                              reference_link_title="very nice again")
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.api+json')

    def test_search_return_list(self):
        search_base_url = "/api/references/?url={}"
        # First reference
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                             url='www.przypis.pl', reference_link="www.przypispowszechny.com",
                                             reference_link_title="very nice again",
                                             create_date=timezone.now() + timedelta(seconds=-1000))
        reference.create_date = timezone.now() + timedelta(seconds=1000)
        reference.save()
        reference = Reference.objects.get(id=reference.id)

        # Second reference
        reference2 = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                              url='www.przypis.pl',
                                              reference_link="www.przypispowszechny2.com",
                                              reference_link_title="very nice",
                                              create_date=timezone.now())
        reference2.save()

        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).count()
        useful_count2 = UserReferenceFeedback.objects.filter(reference=reference2).count()

        raw_response = self.client.get(search_base_url.format(reference.url))
        response = json.loads(raw_response.content.decode('utf8'))['data']
        response_reference = next(row for row in response if str(row['id']) == str(reference.id))
        response_reference2 = next(row for row in response if str(row['id']) == str(reference2.id))
        self.assertEqual(
            response_reference,
            {'id': str(reference.id),
             'type': 'references',
             'attributes': {
                 'url': reference.url,
                 'ranges': reference.ranges,
                 'quote': reference.quote,
                 'priority': reference.priority,
                 'comment': reference.comment,
                 'reference_link': reference.reference_link,
                 'reference_link_title': reference.reference_link_title,
                 'useful': bool(urf),
                 'useful_count': useful_count,
                 'does_belong_to_user': True,
             },
             'relationships': {
                 'user': {
                     'links': {
                         'related': reverse('api:reference_user', kwargs={'reference_id': reference.id})
                     },
                     'data': {'type': 'users', 'id': str(self.user.id)}
                 },
                 'useful': {
                     'links': {
                         'related': reverse('api:reference_useful', kwargs={'reference_id': reference.id})
                     },
                     'data': {'type': 'usefuls', 'id': str(urf.id)}
                 },
                 'reference_reports': {
                     'links': {
                         'related': reverse('api:reference_reports', kwargs={'reference_id': reference.id})
                     },
                     'data': []
                 },
             },
             'links': {
                 'self': reverse('api:reference', kwargs={'reference_id': reference.id})
             }
             })

        self.assertEqual(
            response_reference2,
            {'id': str(reference2.id),
             'type': 'references',
             'attributes': {
                 'url': reference2.url,
                 'ranges': reference2.ranges,
                 'quote': reference2.quote,
                 'priority': reference2.priority,
                 'comment': reference2.comment,
                 'reference_link': reference2.reference_link,
                 'reference_link_title': reference2.reference_link_title,
                 'useful': False,
                 'useful_count': useful_count2,
                 'does_belong_to_user': True,
             },
             'relationships': {
                 'user': {
                        'links': {
                            'related': reverse('api:reference_user', kwargs={'reference_id': reference2.id})
                        },
                     'data': {'type': 'users', 'id': str(self.user.id)}
                 },
                 'useful': {
                     'links': {
                         'related': reverse('api:reference_useful', kwargs={'reference_id': reference2.id})
                     },
                     'data': None
                 },
                 'reference_reports': {
                     'links': {
                         'related': reverse('api:reference_reports', kwargs={'reference_id': reference2.id})
                     },
                     'data': []
                 },
             },
             'links': {
                 'self': reverse('api:reference', kwargs={'reference_id': reference2.id})
             },
             })

    def test_post_new_reference(self):
        base_url = "/api/references/"

        response = self.client.post(
            base_url,
            json.dumps({
                'data': {
                    'type': 'references',
                    'attributes': {
                        'url': "www.przypis.pl",
                        'ranges': "Od tad do tad",
                        'quote': 'very nice',
                        'priority': 'NORMAL',
                        'comment': "komentarz",
                        'reference_link': 'www.przypispowszechny.com',
                        'reference_link_title': 'very nice too',
                    },
                }
            }),
            content_type='application/vnd.api+json')

        self.assertEqual(response.status_code, 200, msg=response.data)
        reference = Reference.objects.get(user=self.user)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).count()
        self.assertEqual(reference.ranges, "Od tad do tad")
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(reference.id),
                    'type': 'references',
                    'attributes': {
                        'url': reference.url,
                        'ranges': reference.ranges,
                        'quote': reference.quote,
                        'priority': reference.priority,
                        'comment': reference.comment,
                        'reference_link': reference.reference_link,
                        'reference_link_title': reference.reference_link_title,
                        'useful': False,
                        'useful_count': useful_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                        'links': {
                            'related': reverse('api:reference_user', kwargs={'reference_id': reference.id})
                        },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'useful': {
                            'links': {
                                'related': reverse('api:reference_useful', kwargs={'reference_id': reference.id})
                            },
                            'data': None
                        },
                        'reference_reports': {
                            'links': {
                                'related': reverse('api:reference_reports', kwargs={'reference_id': reference.id})
                            },
                            'data': []
                        },
                    }
                }
            }
        )

    def test_post_new_reference_with_null_request_reference(self):
        base_url = "/api/references/"

        reference_request = ReferenceRequest.objects.create(
            user=self.user,
            ranges="Od tad do tad",
            quote='very nice',
        )

        response = self.client.post(
            base_url,
            json.dumps({
                'data': {
                    'type': 'references',
                    'attributes': {
                        'url': "www.przypis.pl",
                        'ranges': "Od tad do tad",
                        'quote': 'very nice',
                        'priority': 'NORMAL',
                        'comment': "komentarz",
                        'reference_link': 'www.przypispowszechny.com',
                        'reference_link_title': 'very nice too',
                    }
                }
            }),
            content_type='application/vnd.api+json')

        self.assertEqual(response.status_code, 200, msg=response.data)
        reference = Reference.objects.get(user=self.user)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).count()
        self.assertEqual(reference.ranges, "Od tad do tad")
        self.assertDictEqual(
            json.loads(response.content.decode('utf8')),
            {
                'data': {
                    'id': str(reference.id),
                    'type': 'references',
                    'attributes': {
                        'url': reference.url,
                        'ranges': reference.ranges,
                        'quote': reference.quote,
                        'priority': reference.priority,
                        'comment': reference.comment,
                        'reference_link': reference.reference_link,
                        'reference_link_title': reference.reference_link_title,
                        'useful': False,
                        'useful_count': useful_count,
                        'does_belong_to_user': True,
                    },
                    'relationships': {
                        'user': {
                        'links': {
                            'related': reverse('api:reference_user', kwargs={'reference_id': reference.id})
                        },
                            'data': {'type': 'users', 'id': str(self.user.id)}
                        },
                        'useful': {
                            'links': {
                                'related': reverse('api:reference_useful', kwargs={'reference_id': reference.id})
                            },
                            'data': None
                        },
                        'reference_reports': {
                            'links': {
                                'related': reverse('api:reference_reports', kwargs={'reference_id': reference.id})
                            },
                            'data': []
                        },
                    }
                }
            }
        )

    def test_patch_reference(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', url='www.przypis.pl',
                                             comment="good job",
                                             reference_link="www.przypispowszechny.com",
                                             reference_link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference)
        put_string = 'not so well'
        put_data = json.dumps({
            'data': {
                'id': reference.id,
                'type': 'references',
                'attributes': {
                    'reference_link_title': put_string
                }
            }
        })
        response = self.client.patch(self.base_url.format(reference.id), put_data,
                                     content_type='application/vnd.api+json')
        reference = Reference.objects.get(id=reference.id)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reference.reference_link_title, put_string)
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            {
                'id': str(reference.id),
                'type': 'references',
                'attributes': {
                    'url': reference.url,
                    'ranges': reference.ranges,
                    'quote': reference.quote,
                    'priority': reference.priority,
                    'comment': reference.comment,
                    'reference_link': reference.reference_link,
                    'reference_link_title': reference.reference_link_title,
                    'useful': bool(urf),
                    'useful_count': useful_count,
                    'does_belong_to_user': True,
                },
                'relationships': {
                    'user': {
                        'links': {
                            'related': reverse('api:reference_user', kwargs={'reference_id': reference.id})
                        },
                        'data': {'type': 'users', 'id': str(self.user.id)}
                    },
                    'useful': {
                        'links': {
                            'related': reverse('api:reference_useful', kwargs={'reference_id': reference.id})
                        },
                        'data': {'id': str(urf.id), 'type': get_resource_name(urf, always_single=True)}
                    },
                    'reference_reports': {
                        'links': {
                            'related': reverse('api:reference_reports', kwargs={'reference_id': reference.id})
                        },
                        'data': []
                    },
                }
            }

        )

    def test_patch_inaccessible_field_reference(self):
        reference = Reference.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            reference_link="www.przypispowszechny.com", reference_link_title="very nice",
            quote='not this time'
        )
        UserReferenceFeedback.objects.create(user=self.user, reference=reference)

        put_string = 'not so well'
        put_data = json.dumps({
            'data': {
                'type': 'references',
                'id': reference.id,
                'attributes': {
                    'quote': put_string
                }
            }
        }
        )
        response = self.client.patch(self.base_url.format(reference.id), put_data,
                                     content_type='application/vnd.api+json')
        reference = Reference.objects.get(id=reference.id)
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(reference.comment, put_string)

    def test_delete_reference(self):
        reference = Reference.objects.create(
            user=self.user, priority='NORMAL', url='www.przypis.pl', comment="good job",
            reference_link="www.przypispowszechny.com", reference_link_title="very nice",
            quote='not this time'
        )
        UserReferenceFeedback.objects.create(user=self.user, reference=reference)

        good_id = reference.id
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
