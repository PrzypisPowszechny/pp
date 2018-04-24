from apps.pp.models import UserReferenceFeedback
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedback, Feedback, FeedbackList


class ObjectionResource(object):
    resource_attr = 'objection'
    resource_name = UserReferenceFeedback.JSONAPIMeta.objection_resource_name


class ReferenceRelatedObjection(ObjectionResource, ReferenceRelatedReferenceFeedback):
    pass


# TODO: add test
class ObjectionSingle(ObjectionResource, Feedback):
    pass


# TODO: add test
class ObjectionList(ObjectionResource, FeedbackList):
    pass
