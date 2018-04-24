from apps.pp.models import UserReferenceFeedback
from apps.pp.views.reference_feedbacks import ReferenceFeedbackChange, Feedback, FeedbackList


class ObjectionResource(object):
    resource_attr = 'objection'
    resource_name = UserReferenceFeedback.JSONAPIMeta.objection_resource_name


class ReferenceObjectionChange(ObjectionResource, ReferenceFeedbackChange):
    pass


class Objection(ObjectionResource, Feedback):
    pass


class ObjectionList(ObjectionResource, FeedbackList):
    pass
