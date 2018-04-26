from apps.pp.serializers import ObjectionSerializer
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedbackSingle, FeedbackSingle, FeedbackList


class ObjectionResource(object):
    resource_attr = 'objection'
    serializer_class = ObjectionSerializer


class ReferenceRelatedObjectionSingle(ObjectionResource, ReferenceRelatedReferenceFeedbackSingle):
    pass


# TODO: add test
class ObjectionSingle(ObjectionResource, FeedbackSingle):
    pass


# TODO: add test
class ObjectionList(ObjectionResource, FeedbackList):
    pass
