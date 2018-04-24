from apps.pp.models import UserReferenceFeedback
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedbackSingle, FeedbackSingle, FeedbackList


class UsefulResource(object):
    resource_attr = 'useful'
    resource_name = UserReferenceFeedback.JSONAPIMeta.useful_resource_name


class ReferenceRelatedUsefulSingle(UsefulResource, ReferenceRelatedReferenceFeedbackSingle):
    pass


# TODO: add test
class UsefulSingle(UsefulResource, FeedbackSingle):
    pass


# TODO: add test
class UsefulList(UsefulResource, FeedbackList):
    pass
