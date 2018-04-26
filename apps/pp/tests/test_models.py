from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.pp.models import Reference, AnnotationUpvote, UserAnnotationRequestFeedback, AnnotationRequest


class UserModelTest(TestCase):
    def test_string_representation(self):
        user = get_user_model().objects.create_user(username="Alibaba")
        self.assertEqual(str(user), user.username)

    def test_creating_multiple_users(self):
        for i in range(40):
            get_user_model().objects.create_user(username="Rozbojnik_" + str(i + 1))
        self.assertEqual(40, get_user_model().objects.count())


class AnnotationUpvoteModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="Alibaba")
        cls.user2 = get_user_model().objects.create_user(username="Rozbójnik")
        cls.reference = Reference.objects.create(user=cls.user, priority='NORMAL', comment="good job",
                                                 reference_link="www.przypispowszechny.com",
                                                 reference_link_title="very nice")

    def test_creating(self):
        AnnotationUpvote.objects.create(user=self.user, reference=self.reference)
        self.assertEqual(1, AnnotationUpvote.objects.count())


    def test_updating_annotation_upvote_count(self):
        AnnotationUpvote.objects.create(user=self.user2, reference=self.reference)
        self.reference.count_upvote()
        self.assertEqual(1, self.reference.upvote_count)


class UserAnnotationRequestFeedbackModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="Alibaba")

    def test_creating(self):
        rr = AnnotationRequest.objects.create(user=self.user)
        UserAnnotationRequestFeedback.objects.create(user=self.user, annotation_request=rr, )
        self.assertEqual(1, UserAnnotationRequestFeedback.objects.count())
