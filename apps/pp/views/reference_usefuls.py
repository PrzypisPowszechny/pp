from apps.pp.models import UserReferenceFeedback
from apps.pp.views.reference_feedbacks import ReferenceFeedbackChange, Feedback, FeedbackList


class UsefulResource(object):
    resource_attr = 'useful'
    resource_name = UserReferenceFeedback.JSONAPIMeta.useful_resource_name


class ReferenceUsefulChange(UsefulResource, ReferenceFeedbackChange):
    pass


class Useful(UsefulResource, Feedback):
    pass


class UsefulList(UsefulResource, FeedbackList):
    pass
