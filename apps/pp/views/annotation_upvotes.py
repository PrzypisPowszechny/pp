from apps.pp.serializers import UpvoteSerializer
from apps.pp.views.annotation_feedbacks import AnnotationRelatedAnnotationFeedbackSingle, FeedbackSingle, FeedbackList


class UpvoteResource(object):
    resource_attr = None
    serializer_class = UpvoteSerializer


class AnnotationRelatedUpvoteSingle(UpvoteResource, AnnotationRelatedAnnotationFeedbackSingle):
    pass


# TODO: add test
class UpvoteSingle(UpvoteResource, FeedbackSingle):
    pass


# TODO: add test
class UpvoteList(UpvoteResource, FeedbackList):
    pass
