import django_filters
from django.apps import apps
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.api.permissions import OnlyOwnerCanWrite
from ..filters import BooleanFilter, RequestUserBooleanFilter, StandardizedURLFilterBackend
from ..mails import notify_editors_about_annotation_request
from ..models import AnnotationRequest
from ..serializers import AnnotationRequestSerializer


class AnnotationRequestFilterSet(django_filters.FilterSet):
    answered = BooleanFilter(field_name='annotation', lookup_expr='isnull', exclude=True)
    belongs_to_me = RequestUserBooleanFilter(field_name='user')

    class Meta:
        model = apps.get_model('annotation.AnnotationRequest')
        fields = []


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=StandardizedURLFilterBackend.get_manual_parameters()
))
class AnnotationRequestViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):

    serializer_class = AnnotationRequestSerializer
    queryset = AnnotationRequest.objects.filter(active=True).prefetch_related('annotation_set')
    permission_classes = [OnlyOwnerCanWrite]
    owner_field = 'user'

    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend, StandardizedURLFilterBackend)
    ordering_fields = ('create_date',)
    ordering = "-create_date"
    filterset_class = AnnotationRequestFilterSet
    url_filter_model_field = 'url_id'

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        notify_editors_about_annotation_request(instance)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()

