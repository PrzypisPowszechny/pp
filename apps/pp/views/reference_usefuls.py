from apps.pp.models import UserReferenceFeedback
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedback, Feedback, FeedbackList


class UsefulResource(object):
    resource_attr = 'useful'
    resource_name = UserReferenceFeedback.JSONAPIMeta.useful_resource_name


class ReferenceRelatedUseful(UsefulResource, ReferenceRelatedReferenceFeedback):
    pass


# TODO: add test
class UsefulSingle(UsefulResource, Feedback):
    pass


# TODO: add test
class UsefulList(UsefulResource, FeedbackList):
    pass
