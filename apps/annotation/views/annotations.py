import logging

import django_filters
from django.apps import apps
from django.db.models import Prefetch, Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation import serializers
from apps.annotation.filters import StandardizedURLFilterBackend, ConflictingFilterValueError, ListORFilter
from apps.annotation.models import Annotation, AnnotationUpvote, AnnotationReport, AnnotationRequest
from apps.api.responses import PermissionDenied, ValidationErrorResponse, ErrorResponse, NotFoundResponse, \
    Forbidden

logger = logging.getLogger('pp.annotation')


class AnnotationSingle(APIView):

    @swagger_auto_schema(responses={200: serializers.AnnotationSerializer})
    def get(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(active=True, id=annotation_id)
            upvote = AnnotationUpvote.objects.filter(annotation=annotation, user=request.user).first()
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist):
            return NotFoundResponse()

        return Response(serializers.AnnotationSerializer(
            instance={
                'id': annotation,
                'attributes': annotation,
                'relationships': {
                    'user': annotation.user_id,
                    'annotation_upvote': upvote,
                    'annotation_reports': reports,
                    'annotation_request': annotation.annotation_request_id,
                }},
            context={'request': request, 'root_resource_obj': annotation}
        ).data)

    @swagger_auto_schema(request_body=serializers.AnnotationPatchDeserializer,
                         responses={200: serializers.AnnotationSerializer})
    def patch(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(active=True, id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()
        # Check permissions
        if annotation.user_id != request.user.id:
            return PermissionDenied()
        deserializer = serializers.AnnotationPatchDeserializer(data=request.data, context={'request': request},
                                                               partial=True)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        if 'relationships' in request.data:
            return Forbidden(error_details='Updating relationships not supported')

        patched_data = deserializer.validated_data.get('attributes', {})
        if not patched_data:
            return ErrorResponse()
        for k, v in patched_data.items():
            setattr(annotation, k, v)
        annotation.save()

        feedback = AnnotationUpvote.objects.filter(annotation=annotation, user=request.user).first()
        reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)

        return Response(serializers.AnnotationSerializer(
            instance={
                'id': annotation,
                'attributes': annotation,
                'relationships': {
                    'user': annotation.user_id,
                    'annotation_upvote': feedback,
                    'annotation_reports': reports,
                    'annotation_request': annotation.annotation_request_id,
                }
            },
            context={'request': request, 'root_resource_obj': annotation}
        ).data)

    def delete(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()

        # Check permissions
        if annotation.user_id != request.user.id:
            return PermissionDenied()

        if annotation.active:
            annotation.active = False
            annotation.save()
        return Response()


class AnnotationListFilter(django_filters.FilterSet):
    check_status = ListORFilter(field_name='check_status')

    class Meta:
        model = apps.get_model('annotation.Annotation')
        fields = ['check_status']


class AnnotationList(GenericAPIView):
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend, StandardizedURLFilterBackend)
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"
    filter_class = AnnotationListFilter

    @swagger_auto_schema(request_body=serializers.AnnotationDeserializer,
                         responses={200: serializers.AnnotationSerializer})
    def post(self, request):
        deserializer = serializers.AnnotationDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        annotation_request_id = deserializer.validated_data.get('relationships',  {}).get('annotation_request')
        if annotation_request_id is not None:
            if not AnnotationRequest.objects.filter(active=True).exists():
                raise ErrorResponse('Supplied annotation request does not exist')
        annotation = Annotation(**deserializer.validated_data['attributes'])
        annotation.user_id = request.user.pk
        annotation.annotation_request_id = annotation_request_id
        annotation.save()

        return Response(serializers.AnnotationSerializer(
            instance={
                'id': annotation,
                'attributes': annotation,
                'relationships': {
                    'user': annotation.user_id,
                    'annotation_upvote': None,
                    'annotation_reports': (),
                    'annotation_request': annotation.annotation_request_id
                }
            },
            context={'request': request, 'root_resource_obj': annotation}
        ).data)

    def get_queryset(self):
        queryset = Annotation.objects.filter(active=True).annotate(
            total_upvote_count=Count('feedbacks__id')
        ).select_related(
            'user', 'annotation_request'
        ).prefetch_related(
            Prefetch('annotation_reports', queryset=AnnotationReport.objects.filter(user=self.request.user),
                     to_attr='user_annotation_reports')
        )
        return queryset

    def annotate_fetched_queryset(self, queryset):
        # Get ids on the current page
        annotation_ids = set(annotation.id for annotation in queryset)

        # Get annotations that belong to the user
        user_annotation_ids = Annotation.objects \
            .filter(user=self.request.user, id__in=annotation_ids).values_list('id', flat=True)

        # Manually annotate upvote & objection feedbacks for the current user
        feedbacks = AnnotationUpvote.objects.filter(user=self.request.user, annotation_id__in=annotation_ids)
        annotation_to_feedback = {feedback.annotation_id: feedback for feedback in feedbacks}
        for annotation in queryset:
            feedback = annotation_to_feedback.get(annotation.id)
            annotation.upvote_count_except_user = annotation.total_upvote_count - int(bool(feedback))
            annotation.does_belong_to_user = annotation.id in user_annotation_ids
            annotation.user_feedback = feedback
        return queryset

    # Header parameters need to be provided explicitly
    @swagger_auto_schema(responses={200: serializers.AnnotationListSerializer(many=True)},
                         manual_parameters=StandardizedURLFilterBackend.get_manual_parameters())
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ConflictingFilterValueError as e:
            return ValidationErrorResponse(e.errors)

        queryset = self.paginator.paginate_queryset(queryset, request)

        queryset = self.annotate_fetched_queryset(queryset)

        return self.get_paginated_response([
            serializers.AnnotationListSerializer(instance={
                'id': annotation,
                'attributes': annotation,
                'relationships': {
                    'user': annotation.user_id,
                    'annotation_upvote': annotation.user_feedback,
                    'annotation_reports': annotation.user_annotation_reports,
                    'annotation_request': annotation.annotation_request_id,
                }
            }, context={'request': request, 'root_resource_obj': annotation}).data
            for annotation in queryset])


class AnnotationUpvoteRelatedAnnotationSingle(APIView):

    @swagger_auto_schema(responses={200: serializers.AnnotationSerializer})
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user)
            annotation = Annotation.objects.get(active=True, feedbacks=feedback_id, feedbacks__user=request.user)
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist):
            return NotFoundResponse()
        return Response(serializers.AnnotationSerializer(
            instance={
                'id': annotation,
                'attributes': annotation,
                'relationships': {
                    'user': annotation.user_id,
                    'annotation_upvote': feedback,
                    'annotation_reports': reports,
                    'annotation_request': annotation.annotation_request_id,
                }
            },
            context={'request': request, 'root_resource_obj': annotation}
        ).data)


class AnnotationReportRelatedAnnotationSingle(APIView):

    @swagger_auto_schema(responses={200: serializers.AnnotationSerializer})
    def get(self, request, report_id):
        try:
            AnnotationReport.objects.get(id=report_id, user=request.user)
            annotation = Annotation.objects.get(annotation_reports=report_id, active=True,
                                                annotation_reports__user=request.user)
            feedback = AnnotationUpvote.objects.get(annotation_id=annotation.id, user=request.user)
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist, AnnotationReport.DoesNotExist):
            return NotFoundResponse()
        return Response(serializers.AnnotationSerializer(
            instance={
                'id': annotation,
                'attributes': annotation,
                'relationships': {
                    'user': annotation.user_id,
                    'annotation_upvote': feedback,
                    'annotation_reports': reports,
                    'annotation_request': annotation.annotation_request_id,
                }
            },
            context={'request': request, 'root_resource_obj': annotation}
        ).data)
