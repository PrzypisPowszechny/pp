import rest_framework_json_api.parsers
import rest_framework_json_api.renderers
from rest_framework import mixins, viewsets, generics

from apps.annotation import models
from apps.annotation import serializers
from apps.api.permissions import OnlyOwnerCanRead


class AnnotationUpvoteViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = models.AnnotationUpvote.objects.all()
    serializer_class = serializers.AnnotationUpvoteSerializer
    renderer_classes = [rest_framework_json_api.renderers.JSONRenderer]
    parser_classes = [rest_framework_json_api.parsers.JSONParser]
    permission_classes = [OnlyOwnerCanRead]
    owner_field = 'user'


class AnnotationRelatedAnnotationUpvote(generics.RetrieveAPIView):
    queryset = models.AnnotationUpvote.objects.all()
    serializer_class = serializers.AnnotationUpvoteSerializer
    renderer_classes = [rest_framework_json_api.renderers.JSONRenderer]
    parser_classes = [rest_framework_json_api.parsers.JSONParser]
    permission_classes = [OnlyOwnerCanRead]
    owner_field = 'user'

    # Router
    lookup_url_kwarg = 'annotation_id'
    lookup_field = 'annotation'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
