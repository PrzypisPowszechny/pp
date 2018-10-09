import rest_framework
from django.db.models import Case, Prefetch, Count
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation.filters import StandardizedURLFilterBackend, BodyFilterBackend, StandardizedURLBodyFilterBackend, \
    StandardizedURLQueryFilterBackend
from apps.annotation.models import Annotation, AnnotationUpvote, AnnotationReport
from apps.annotation.responses import PermissionDenied, ValidationErrorResponse, ErrorResponse, NotFoundResponse, Forbidden
from apps.annotation.serializers import AnnotationPatchDeserializer, AnnotationListSerializer, AnnotationDeserializer, \
    AnnotationSerializer, SchemaGeneratorSerializer
from apps.annotation.utils import get_resource_name, DataPreSerializer


class AnnotationBase(object):
    def get_pre_serialized_annotation(self, annotation, feedback=None, reports=()):
        pre_serializer = DataPreSerializer(annotation, {'attributes': annotation})
        pre_serializer.set_relation(get_resource_name(annotation.user),
                                    resource_id=annotation.user_id)
        pre_serializer.set_relation(get_resource_name(feedback, model=AnnotationUpvote),
                                    resource_id=feedback)
        pre_serializer.set_relation(get_resource_name(annotation, related_field='annotation_reports'),
                                    resource_id=reports)
        return pre_serializer.data


class AnnotationSingle(AnnotationBase, APIView):
    resource_name = 'annotations'

    @swagger_auto_schema(responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(active=True, id=annotation_id)
            feedback = AnnotationUpvote.objects.filter(annotation=annotation, user=request.user).first()
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist):
            return NotFoundResponse()
        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)

    @swagger_auto_schema(request_body=AnnotationPatchDeserializer,
                         responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user)
    def patch(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(active=True, id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()
        # Check permissions
        if annotation.user_id != request.user.id:
            return PermissionDenied()
        deserializer = AnnotationPatchDeserializer(data=request.data, context={'request': request}, partial=True)
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

        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)

    @method_decorator(allow_lazy_user)
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


class AnnotationListBase(AnnotationBase, GenericAPIView):
    # A base class for use by the "normal" view (in REST and JSON-API standards) as well as the confidential one
    resource_name = 'annotations'
    pagination_class = LimitOffsetPagination
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"


    def get_queryset(self):
        queryset = Annotation.objects.filter(active=True).annotate(
            total_upvote_count=Count('feedbacks__id')
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

    def pre_serialize_queryset(self, queryset):
        return [
            self.get_pre_serialized_annotation(annotation, annotation.user_feedback, annotation.user_annotation_reports)
            for annotation in queryset]

    def get_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.paginator.paginate_queryset(queryset, request)

        queryset = self.annotate_fetched_queryset(queryset)

        data_list = self.pre_serialize_queryset(queryset)

        return self.get_paginated_response(
            AnnotationListSerializer(data_list, many=True, context={'request': request}).data
        )


class AnnotationSensitiveSchemaGeneratorDeserializer(SchemaGeneratorSerializer):
    url = serializers.CharField(required=False)


class AnnotationListSensitive(AnnotationListBase):
    # A very specific view for reading annotations with a POST request while by REST standards it would normally be
    # implemented as GET since it does not modify anything.
    #
    # We implement is also as POST for even more secure reads (since URL browsing history is sensitive)

    filter_backends = (OrderingFilter, DjangoFilterBackend, StandardizedURLBodyFilterBackend)
    filter_fields = ()

    @swagger_auto_schema(request_body=AnnotationSensitiveSchemaGeneratorDeserializer,
                         responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request, *args, **kwargs):
        return super().get_list(request, *args, **kwargs)


class AnnotationList(AnnotationListBase):
    filter_backends = (OrderingFilter, DjangoFilterBackend, StandardizedURLQueryFilterBackend)
    filter_fields = ()

    @swagger_auto_schema(request_body=AnnotationDeserializer,
                         responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = AnnotationDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        annotation = Annotation(**deserializer.validated_data['attributes'])
        annotation.user_id = request.user.pk
        annotation.save()

        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation),
                                             context={'request': request}).data)

    @swagger_auto_schema(responses={200: AnnotationListSerializer(many=True)})
    @method_decorator(allow_lazy_user)
    def get(self, request, *args, **kwargs):
        return super().get_list(request, *args, **kwargs)


class AnnotationFeedbackRelatedAnnotationSingle(AnnotationBase, APIView):
    resource_attr = None

    @swagger_auto_schema(responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                    **({self.resource_attr: True} if self.resource_attr else {}))
            annotation = Annotation.objects.get(active=True, feedbacks=feedback_id, feedbacks__user=request.user)
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist):
            return NotFoundResponse()
        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)


class AnnotationUpvoteRelatedAnnotationSingle(AnnotationFeedbackRelatedAnnotationSingle):
    resource_attr = None


class AnnotationReportRelatedAnnotationSingle(AnnotationBase, APIView):

    @swagger_auto_schema(responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, report_id):
        try:
            AnnotationReport.objects.get(id=report_id, user=request.user)
            annotation = Annotation.objects.get(annotation_reports=report_id, active=True,
                                                annotation_reports__user=request.user)
            feedback = AnnotationUpvote.objects.get(annotation_id=annotation.id, user=request.user)
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist, AnnotationReport.DoesNotExist):
            return NotFoundResponse()
        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)
