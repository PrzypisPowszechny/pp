from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.pp.models import Reference, UserReferenceFeedback, UserReferenceRequestFeedback, ReferenceRequest


class UserModelTest(TestCase):
    def test_string_representation(self):
        user = get_user_model().objects.create_user(username="Alibaba")
        self.assertEqual(str(user), user.username)

    def test_creating_multiple_users(self):
        for i in range(40):
            get_user_model().objects.create_user(username="Rozbojnik_" + str(i + 1))
        self.assertEqual(40, get_user_model().objects.count())


class UserReferenceFeedbackModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="Alibaba")
        cls.user2 = get_user_model().objects.create_user(username="Rozbójnik")
        cls.reference = Reference.objects.create(user=cls.user, priority='NORMAL', comment="good job",
                                                 reference_link="www.przypispowszechny.com",
                                                 reference_link_title="very nice")

    def test_creating(self):
        UserReferenceFeedback.objects.create(user=self.user, reference=self.reference)
        self.assertEqual(1, UserReferenceFeedback.objects.count())


    def test_updating_reference_useful_count(self):
        UserReferenceFeedback.objects.create(user=self.user2, reference=self.reference)
        self.reference.count_useful()
        self.assertEqual(1, self.reference.useful_count)


class UserReferenceRequestFeedbackModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="Alibaba")

    def test_creating(self):
        rr = ReferenceRequest.objects.create(user=self.user)
        UserReferenceRequestFeedback.objects.create(user=self.user, reference_request=rr, )
        self.assertEqual(1, UserReferenceRequestFeedback.objects.count())
