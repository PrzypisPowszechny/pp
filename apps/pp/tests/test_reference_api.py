import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.pp.models import Reference, UserReferenceFeedback


class PPAPITest(TestCase):
    base_url = "/annotations/{}/"
    maxDiff = None

    def test_get_returns_json_200(self):
        user = get_user_model().objects.create_user(username="Alibaba")
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        response = self.client.get(self.base_url.format(reference.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_returns_reference(self):
        user = get_user_model().objects.create_user(username="Alibaba", password='12345')
        # token = Token.objects.create(user=user)
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        self.client.login(username=user, password='12345')
        self.assertEqual(1, urf.useful)
        response = self.client.get(self.base_url.format(reference.id))
        reference.count_useful_and_objection()
        print(response.content.decode('utf8'))
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
             'useful_count': reference.useful_count,
             'objection': urf.objection,
             'objection_count': reference.objection_count}
        )

    def test_get_wrong_url(self):
        response = self.client.get(self.base_url.format(123))
        self.assertEqual(response.status_code, 404)

    def test_search_return_json_200(self):
        base_url2 = "/annotations/search&url={}"
        user = get_user_model().objects.create_user(username="Alibaba")
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        reference2 = Reference.objects.create(user=user, priority='NORMAL', comment="more good job",
                                              link="www.przypispowszechny.com", link_title="very nice again")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        response = self.client.get(base_url2.format(reference.link))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_search_return_list(self):
        base_url2 = "/annotations/search&url={}"
        user = get_user_model().objects.create_user(username="Alibaba", password='12345')
        reference2 = Reference.objects.create(user=user, priority='NORMAL', comment="good job", url='www.przypis.pl',
                                              link="www.przypispowszechny2.com", link_title="very nice",
                                              create_date=datetime.now())
        reference2.save()

        urf2 = UserReferenceFeedback.objects.create(user=user, reference=reference2, useful=False, objection=False)
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="more good job",
                                             url='www.przypis.pl', link="www.przypispowszechny.com",
                                             link_title="very nice again",
                                             create_date=datetime.now() + timedelta(seconds=-1000))
        reference.save()
        reference.create_date = datetime.now() + timedelta(seconds=1000)
        reference.save()
        reference = Reference.objects.get(id=reference.id)
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        self.client.login(username=user, password='12345')
        reference.count_useful_and_objection()
        reference2.count_useful_and_objection()
        response = self.client.get(base_url2.format(reference.url))
        test_answesr = {
            'total': 2,
            'rows': [
                {'id': reference.id,
                 'url': reference.url,
                 'range': reference.range,
                 'quote': reference.quote,
                 'priority': reference.priority,
                 'link': reference.link,
                 'link_title': reference.link_title,
                 'useful': urf.useful,
                 'useful_count': reference.useful_count,
                 'objection': urf.objection,
                 'objection_count': reference.objection_count
                 },
                {'id': reference2.id,
                 'url': reference2.url,
                 'range': reference2.range,
                 'quote': reference2.quote,
                 'priority': reference2.priority,
                 'link': reference2.link,
                 'link_title': reference2.link_title,
                 'useful': urf2.useful,
                 'useful_count': reference2.useful_count,
                 'objection': urf2.objection,
                 'objection_count': reference2.objection_count
                 }
            ]
        }
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            test_answesr)

    def test_search_url_without_references(self):
        base_url2 = "/annotations/search&url={}"
        total = 0
        rows = []
        url = "www.przypis.pl"
        test_answear = {
            'total': total,
            'rows': rows
        }
        response = self.client.get(base_url2.format(url))
        self.assertEqual(
            json.loads(response.content.decode('utf8'))['data'],
            test_answear
        )

    def test_post_new_reference(self):
        base_url3 = "/annotations/"
        user = get_user_model().objects.create_user(username="Alibaba", password='12345')
        self.client.login(username=user, password='12345')
        response = self.client.post(
            base_url3, json.dumps(
                {
                    'url': "www.przypis.pl",
                    'range': "Od tad do tad",
                    'quote': 'very nice',
                    'priority': 'NORMAL',
                    'link': 'www.przypispowszechny.com',
                    'link_title': 'very nice too'}), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        reference = Reference.objects.get(user=user)
        reference.count_useful_and_objection()
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
             'useful': 0,
             'useful_count': reference.useful_count,
             'objection': 0,
             'objection_count': reference.objection_count}
        )

    def test_patch_reference(self):
        user = get_user_model().objects.create_user(username="Alibaba", password='12345')
        self.client.login(username=user, password='12345')
        reference = Reference.objects.create(user=user, priority='NORMAL', url='www.przypis.pl', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        put_string = 'not so well'
        put_data = json.dumps({
            'link_title': put_string,
        })
        response = self.client.patch(self.base_url.format(reference.id), put_data, content_type='application/json')
        reference = Reference.objects.get(id=reference.id)
        reference.count_useful_and_objection()
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
             'useful_count': reference.useful_count,
             'objection': urf.objection,
             'objection_count': reference.objection_count}
        )

    def test_patch_wrong_field_reference(self):
        user = get_user_model().objects.create_user(username="Alibaba", password='12345')
        self.client.login(username=user, password='12345')
        reference = Reference.objects.create(user=user, priority='NORMAL', url='www.przypis.pl', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        put_string = 'not so well'
        put_data = json.dumps({
            'comment': put_string,
        })
        response = self.client.patch(self.base_url.format(reference.id), put_data, content_type='application/json')
        reference = Reference.objects.get(id=reference.id)
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(reference.comment, put_string)

    def test_delete_reference(self):
        user = get_user_model().objects.create_user(username="Alibaba", password='12345')
        # token = Token.objects.create(user=user)
        self.client.login(username=user, password='12345')
        reference = Reference.objects.create(user=user, priority='NORMAL', url='www.przypis.pl', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice",
                                             quote='not this time')
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        id = reference.id
        response = self.client.delete(self.base_url.format(reference.id), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response2 = self.client.get(self.base_url.format(id))
        self.assertEqual(response2.status_code, 404)
