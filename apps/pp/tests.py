from django.test import TestCase
from .models import Reference, User, UserReferenceFeedback, UserReferenceRequestFeedback, ReferenceRequest


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


class UserReferenceRequestFeedbackModelTest(TestCase):
    def test_creating_userreferencerequestfeedback(self):
        user = User.objects.create_user(username="Alibaba")
        rr = ReferenceRequest.objects.create(user=user)
        urrf = UserReferenceRequestFeedback.objects.create(user=user, reference_request=rr)
        self.assertEqual(1, UserReferenceRequestFeedback.objects.count())
