from apps.pp.serializers import UpvoteSerializer
from apps.pp.views.reference_feedbacks import ReferenceRelatedReferenceFeedbackSingle, FeedbackSingle, FeedbackList


class UpvoteResource(object):
    resource_attr = None
    serializer_class = UpvoteSerializer


class ReferenceRelatedUpvoteSingle(UpvoteResource, ReferenceRelatedReferenceFeedbackSingle):
    pass


# TODO: add test
class UpvoteSingle(UpvoteResource, FeedbackSingle):
    pass


# TODO: add test
class UpvoteList(UpvoteResource, FeedbackList):
    pass
