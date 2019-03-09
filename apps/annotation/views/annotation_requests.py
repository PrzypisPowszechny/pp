from django_filters import OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation.mails import notify_editors_about_annotation_request
from apps.annotation.models import AnnotationRequest
from apps.annotation.serializers import AnnotationRequestDeserializer, AnnotationRequestSerializer
from apps.api.responses import ValidationErrorResponse


class AnnotationRequests(GenericAPIView):
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"

    @swagger_auto_schema(request_body=AnnotationRequestDeserializer,
                         responses={200: AnnotationRequestSerializer})
    def post(self, request):
        deserializer = AnnotationRequestDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        data = deserializer.validated_data['attributes']

        annotation_request = AnnotationRequest(**data)
        annotation_request.user_id = request.user.pk
        annotation_request.save()

        notify_editors_about_annotation_request(annotation_request)

    @swagger_auto_schema(responses={200: AnnotationRequestSerializer(many=True)})
    def get(self, request):
        queryset = AnnotationRequest.objects.filter(active=True).prefetch_related('annotation_set')

        queryset = self.paginator.paginate_queryset(queryset, request)

        return self.get_paginated_response([
            AnnotationRequestSerializer(instance={
                'id': annotation_request,
                'attributes': annotation_request,
                'relationships': {
                    'annotations': list(annotation_request.annotation_set.all())
                }
            }, context={'request': request, 'root_resource_obj': annotation_request}).data
            for annotation_request in queryset])
