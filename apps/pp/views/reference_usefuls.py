from apps.pp.serializers import UsefulSerializer
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedbackSingle, FeedbackSingle, FeedbackList


class UsefulResource(object):
    resource_attr = 'useful'
    serializer_class = UsefulSerializer


class ReferenceRelatedUsefulSingle(UsefulResource, ReferenceRelatedReferenceFeedbackSingle):
    pass


# TODO: add test
class UsefulSingle(UsefulResource, FeedbackSingle):
    pass


# TODO: add test
class UsefulList(UsefulResource, FeedbackList):
    pass
