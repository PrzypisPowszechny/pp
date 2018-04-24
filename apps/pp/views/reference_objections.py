from apps.pp.models import UserReferenceFeedback
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedbackSingle, FeedbackSingle, FeedbackList


class ObjectionResource(object):
    resource_attr = 'objection'
    resource_name = UserReferenceFeedback.JSONAPIMeta.objection_resource_name


class ReferenceRelatedObjectionSingle(ObjectionResource, ReferenceRelatedReferenceFeedbackSingle):
    pass


# TODO: add test
class ObjectionSingle(ObjectionResource, FeedbackSingle):
    pass


# TODO: add test
class ObjectionList(ObjectionResource, FeedbackList):
    pass
