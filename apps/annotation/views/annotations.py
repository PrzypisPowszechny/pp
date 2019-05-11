import logging

import django_filters
from django.apps import apps
from django.db.models import Count, Prefetch
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation import serializers
from apps.annotation.filters import StandardizedURLFilterBackend, ListORFilter
from apps.annotation.models import Annotation, AnnotationUpvote
from apps.api.permissions import OnlyEditorCanWrite, OnlyOwnerCanWrite
from apps.docs.utils import unless_swagger

logger = logging.getLogger('pp.annotation')


class AnnotationListFilter(django_filters.FilterSet):
    check_status = ListORFilter()

    class Meta:
        model = apps.get_model('annotation.Annotation')
        fields = ['check_status']


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=StandardizedURLFilterBackend.get_manual_parameters()
))
class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.filter(active=True)
    permission_classes = (OnlyEditorCanWrite & OnlyOwnerCanWrite,)
    owner_field = 'user'

    # List related definitions
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend, StandardizedURLFilterBackend)
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"
    filter_class = AnnotationListFilter
    url_filter_model_field = 'url_id'

    # Router
    lookup_url_kwarg = 'annotation_id'

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return serializers.AnnotationPatchSerializer
        else:
            return serializers.AnnotationSerializer

    def get_queryset(self):
        return super().get_queryset().annotate(
            total_upvote_count=Count('annotationupvote')
        ).select_related(
            'user', 'annotation_request'
        ).prefetch_related(Prefetch(
            lookup='annotationupvote_set',
            queryset=AnnotationUpvote.objects.filter(
                user=unless_swagger(self, lambda: self.request.user, default=None)
            ),
            to_attr='user_annotation_upvotes'
        ))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # When creating get_queryset is not called, so we need to make it up
        serializer.instance = self.get_queryset().get(id=serializer.instance.id)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()
