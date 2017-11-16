from django.test import TestCase
from .models import Reference, User, UserReferenceFeedback, UserReferenceRequestFeedback, ReferenceRequest
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.core.urlresolvers import reverse
import json


class UserModelTest(TestCase):
    def test_string_representation(self):
        user = User.objects.create_user(username="Alibaba")
        self.assertEqual(str(user), user.username)

    def test_creating_multiple_users(self):
        for i in range(40):
            user = User.objects.create_user(username="Rozbojnik_" + str(i + 1))
        self.assertEqual(40, User.objects.count())


class ReferenceModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="Alibaba")
        self.reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                                  link="www.przypispowszechny.com", link_title="very nice")

    def test_string_representation(self):
        self.assertEqual(self.reference.comment, str(self.reference))

    def test_creating_reference_without_user(self):
        try:
            reference = Reference.objects.create(priority='NORMAL', comment="good job",
                                                 link="www.przypispowszechny.com", link_title="very nice")
        except:
            self.assertEqual(1, 1)
        else:
            self.assertEqual(0, 1)


class UserReferenceFeedbackModelTest(TestCase):
    def test_creating_userreferencefeedback(self):
        user = User.objects.create_user(username="Alibaba")
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=True)
        self.assertEqual(1, UserReferenceFeedback.objects.count())

    def test_useful_userreferencefeedback(self):
        user = User.objects.create_user(username="Alibaba")
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=True)
        urf2 = UserReferenceFeedback.objects.get(user=user, reference=reference)
        self.assertEqual(True, urf2.useful)

    def test_updating_reference_useful_and_objection_count(self):
        user = User.objects.create_user(username="Alibaba")
        user2 = User.objects.create_user(username="Rozbojnik")
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=True)
        UserReferenceFeedback.objects.create(user=user2, reference=reference, useful=True, objection=False)
        reference.count_useful_and_objection()
        self.assertEqual(2, reference.useful_count)
        self.assertEqual(1, reference.objection_count)


class UserReferenceRequestFeedbackModelTest(TestCase):
    def test_creating_userreferencerequestfeedback(self):
        user = User.objects.create_user(username="Alibaba")
        rr = ReferenceRequest.objects.create(user=user)
        urrf = UserReferenceRequestFeedback.objects.create(user=user, reference_request=rr, )
        self.assertEqual(1, UserReferenceRequestFeedback.objects.count())


class PPAPITest(APITestCase):
    base_url = "/annotations/{}/"

    def test_get_returns_json_200(self):
        user = User.objects.create_user(username="Alibaba")
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        response = self.client.get(self.base_url.format(reference.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_returns_reference(self):
        user = User.objects.create_user(username="Alibaba", password='12345')
        token = Token.objects.create(user=user)
        reference = Reference.objects.create(user=user, priority='NORMAL', comment="good job",
                                             link="www.przypispowszechny.com", link_title="very nice")
        urf = UserReferenceFeedback.objects.create(user=user, reference=reference, useful=True, objection=False)
        self.client.login(username=user, password='12345', HTTP_AUTHORIZATION=token)
        self.assertEqual(1, urf.useful)
        response = self.client.get(self.base_url.format(reference.id))
        reference.count_useful_and_objection()
        self.assertEqual(
            json.loads(response.content.decode('utf8')),
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
