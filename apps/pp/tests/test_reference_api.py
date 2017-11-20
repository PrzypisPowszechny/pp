import json
from datetime import datetime, timedelta
from django.test import TestCase
from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.tests.utils import create_test_user


class ReferenceAPITest(TestCase):
    base_url = "/annotations/{}/"
    maxDiff = None

    # IMPORTANT: we log in for each test, so self.user has already an open session with server
    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_returns_json_200(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True, objection=False)
        response = self.client.get(self.base_url.format(reference.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_returns_reference(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True, objection=False)
        response = self.client.get(self.base_url.format(reference.id))

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).filter(useful=True).count()
        objection_count = UserReferenceFeedback.objects.filter(reference=reference).filter(objection=True).count()

        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            {'id': reference.id,
             'url': reference.url,
             'range': reference.range,
             'quote': reference.quote,
             'priority': reference.priority,
             'link': reference.link,
             'link_title': reference.link_title,
             'useful': urf.useful,
             'useful_count': useful_count,
             'objection': urf.objection,
             'objection_count': objection_count}
        )

    def test_empty_search_return_json_200(self):
        search_base_url = "/annotations/search&url={}"
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        test_answer = {
            'total': 0,
            'rows': []
        }
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            test_answer
        )


    def test_nonempty_search_return_json_200(self):
        search_base_url = "/annotations/search&url={}"
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        reference2 = Reference.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                              link="www.przypispowszechny.com", link_title="very nice again")
        response = self.client.get(search_base_url.format('przypis powszechny'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')


    def test_search_return_list(self):
        search_base_url = "/annotations/search&url={}"
        # First reference
        reference = Reference.objects.create(user=self.user, priority='NORMAL', comment="more good job",
                                             url='www.przypis.pl', link="www.przypispowszechny.com",
                                             link_title="very nice again",
                                             create_date=datetime.now() + timedelta(seconds=-1000))
        reference.create_date = datetime.now() + timedelta(seconds=1000)
        reference.save()
        reference = Reference.objects.get(id=reference.id)

        # Second reference
        reference2 = Reference.objects.create(user=self.user, priority='NORMAL', comment="good job",
                                              url='www.przypis.pl',
                                              link="www.przypispowszechny2.com", link_title="very nice",
                                              create_date=datetime.now())
        reference2.save()

        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True, objection=False)
        urf2 = UserReferenceFeedback.objects.create(user=self.user, reference=reference2, useful=False, objection=True)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).filter(useful=True).count()
        objection_count = UserReferenceFeedback.objects.filter(reference=reference).filter(objection=True).count()

        useful_count2 = UserReferenceFeedback.objects.filter(reference=reference2).filter(useful=True).count()
        objection_count2 = UserReferenceFeedback.objects.filter(reference=reference2).filter(objection=True).count()

        raw_response = self.client.get(search_base_url.format(reference.url))
        response = json.loads(raw_response.content.decode('utf8'))['data']
        self.assertEquals(response['total'], 2)
        self.assertEquals(len(response['rows']), 2)
        response_reference = next(row for row in response['rows'] if row['id'] == reference.id)
        response_reference2 = next(row for row in response['rows'] if row['id'] == reference2.id)
        self.assertEqual(response_reference,
                         {'id': reference.id,
                          'url': reference.url,
                          'range': reference.range,
                          'quote': reference.quote,
                          'priority': reference.priority,
                          'link': reference.link,
                          'link_title': reference.link_title,
                          'useful': urf.useful,
                          'useful_count': useful_count,
                          'objection': urf.objection,
                          'objection_count': objection_count
                          })
        self.assertEqual(response_reference2,
                         {'id': reference2.id,
                          'url': reference2.url,
                          'range': reference2.range,
                          'quote': reference2.quote,
                          'priority': reference2.priority,
                          'link': reference2.link,
                          'link_title': reference2.link_title,
                          'useful': urf2.useful,
                          'useful_count': useful_count2,
                          'objection': urf2.objection,
                          'objection_count': objection_count2
                          })

    def test_post_new_reference(self):
        base_url = "/annotations/"

        response = self.client.post(
            base_url,
            json.dumps({
                'url': "www.przypis.pl",
                'range': "Od tad do tad",
                'quote': 'very nice',
                'priority': 'NORMAL',
                'link': 'www.przypispowszechny.com',
                'link_title': 'very nice too'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        reference = Reference.objects.get(user=self.user)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).filter(useful=True).count()
        objection_count = UserReferenceFeedback.objects.filter(reference=reference).filter(objection=True).count()

        self.assertEqual(reference.range, "Od tad do tad")
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            {'id': reference.id,
             'url': reference.url,
             'range': reference.range,
             'quote': reference.quote,
             'priority': reference.priority,
             'link': reference.link,
             'link_title': reference.link_title,
             'useful': False,
             'useful_count': useful_count,
             'objection': False,
             'objection_count': objection_count}
        )

    def test_patch_reference(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', url='www.przypis.pl',
                                             comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True, objection=False)
        put_string = 'not so well'
        put_data = json.dumps({
            'link_title': put_string,
        })
        response = self.client.patch(self.base_url.format(reference.id), put_data, content_type='application/json')
        reference = Reference.objects.get(id=reference.id)

        useful_count = UserReferenceFeedback.objects.filter(reference=reference).filter(useful=True).count()
        objection_count = UserReferenceFeedback.objects.filter(reference=reference).filter(objection=True).count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reference.link_title, put_string)
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            {'id': reference.id,
             'url': reference.url,
             'range': reference.range,
             'quote': reference.quote,
             'priority': reference.priority,
             'link': reference.link,
             'link_title': reference.link_title,
             'useful': urf.useful,
             'useful_count': useful_count,
             'objection': urf.objection,
             'objection_count':     objection_count}
        )

    def test_patch_wrong_field_reference(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', url='www.przypis.pl',
                                             comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True, objection=False)
        put_string = 'not so well'
        put_data = json.dumps({
            'comment': put_string,
        })
        response = self.client.patch(self.base_url.format(reference.id), put_data, content_type='application/json')
        reference = Reference.objects.get(id=reference.id)
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(reference.comment, put_string)

    def test_delete_reference(self):
        reference = Reference.objects.create(user=self.user, priority='NORMAL', url='www.przypis.pl',
                                             comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=self.user, reference=reference, useful=True, objection=False)
        id = reference.id
        response = self.client.delete(self.base_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response2 = self.client.get(self.base_url.format(id))
        self.assertEqual(response2.status_code, 404)