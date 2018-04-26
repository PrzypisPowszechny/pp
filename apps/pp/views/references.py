from django.db.models import Case, Prefetch
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.pp.models import Reference, AnnotationUpvote, AnnotationReport
from apps.pp.responses import PermissionDenied, ValidationErrorResponse, ErrorResponse, NotFoundResponse, Forbidden
from apps.pp.serializers import ReferencePatchDeserializer, ReferenceListSerializer, ReferenceDeserializer, \
    ReferenceSerializer
from apps.pp.utils import get_relationship_id, get_resource_name, DataPreSerializer


class ReferenceBase(object):
    def get_pre_serialized_reference(self, reference, feedback=None, reports=()):
        pre_serializer = DataPreSerializer(reference, {'attributes': reference})
        pre_serializer.set_relation(get_resource_name(reference.user),
                                    resource_id=reference.user_id)
        pre_serializer.set_relation(get_resource_name(feedback, model=AnnotationUpvote),
                                    resource_id=feedback)
        pre_serializer.set_relation(get_resource_name(reference, related_field='annotation_reports'),
                                    resource_id=reports)
        return pre_serializer.data


class ReferenceSingle(ReferenceBase, APIView):
    resource_name = 'references'

    @swagger_auto_schema(responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, reference_id):
        try:
            reference = Reference.objects.get(active=True, id=reference_id)
            feedback = AnnotationUpvote.objects.filter(reference=reference, user=request.user).first()
            reports = AnnotationReport.objects.filter(reference_id=reference.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Reference.DoesNotExist):
            return NotFoundResponse()
        return Response(ReferenceSerializer(instance=self.get_pre_serialized_reference(reference, feedback, reports),
                                            context={'request': request}).data)

    @swagger_auto_schema(request_body=ReferencePatchDeserializer,
                         responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def patch(self, request, reference_id):
        try:
            reference = Reference.objects.get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return NotFoundResponse()
        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()
        deserializer = ReferencePatchDeserializer(data=request.data, context={'request': request}, partial=True)
        if not deserializer.is_valid():
            return ErrorResponse(deserializer.errors)
        if 'relationships' in request.data:
            return Forbidden(error_details='Updating relationships not supported')

        patched_data = deserializer.validated_data.get('attributes', {})
        if not patched_data:
            return ErrorResponse()
        for k, v in patched_data.items():
            setattr(reference, k, v)
        reference.save()

        feedback = AnnotationUpvote.objects.filter(reference=reference, user=request.user).first()
        reports = AnnotationReport.objects.filter(reference_id=reference.id, user=request.user)

        return Response(ReferenceSerializer(instance=self.get_pre_serialized_reference(reference, feedback, reports),
                                            context={'request': request}).data)

    @method_decorator(allow_lazy_user)
    def delete(self, request, reference_id):
        try:
            reference = Reference.objects.get(id=reference_id)
        except Reference.DoesNotExist:
            return NotFoundResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()

        if reference.active:
            reference.active = False
            reference.save()
        return Response()


class ReferenceList(ReferenceBase, GenericAPIView):
    resource_name = 'references'
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"
    filter_fields = ('url',)

    @swagger_auto_schema(request_body=ReferenceDeserializer,
                         responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = ReferenceDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        reference = Reference(**deserializer.validated_data['attributes'])
        reference.user_id = request.user.pk
        reference.save()

        return Response(ReferenceSerializer(instance=self.get_pre_serialized_reference(reference),
                                            context={'request': request}).data)


    def get_queryset(self):
        queryset = Reference.objects \
            .filter(active=True).annotate(
                upvote_count=Coalesce(
                    Sum(Case(When(feedbacks__id=True, then=1)), default=0, output_field=IntegerField()),
                    0),
            ).prefetch_related(
                Prefetch('annotation_reports', queryset=AnnotationReport.objects.filter(user=self.request.user),
                         to_attr='user_annotation_reports')
            )
        return queryset

    def annotate_fetched_queryset(self, queryset):
        # Get ids on the current page
        reference_ids = set(reference.id for reference in queryset)

        # Get references that belong to the user
        user_reference_ids = Reference.objects \
            .filter(user=self.request.user, id__in=reference_ids).values_list('id', flat=True)

        # Manually annotate upvote & objection feedbacks for the current user
        feedbacks = AnnotationUpvote.objects.filter(user=self.request.user, reference_id__in=reference_ids)
        reference_to_feedback = {feedback.reference_id: feedback for feedback in feedbacks}
        for reference in queryset:
            feedback = reference_to_feedback.get(reference.id)
            # TODO: setting upvote and objection attrs duplicates corresponding relationships, consider removing
            reference.upvote = bool(feedback)
            reference.does_belong_to_user = reference.id in user_reference_ids
            reference.user_feedback = feedback
        return queryset

    def pre_serialize_queryset(self, queryset):
        return [self.get_pre_serialized_reference(reference, reference.user_feedback, reference.user_annotation_reports)
                for reference in queryset]

    @swagger_auto_schema(responses={200: ReferenceListSerializer(many=True)})
    @method_decorator(allow_lazy_user)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.paginator.paginate_queryset(queryset, request)

        queryset = self.annotate_fetched_queryset(queryset)

        data_list = self.pre_serialize_queryset(queryset)

        return self.get_paginated_response(ReferenceListSerializer(data_list, many=True).data)


class ReferenceFeedbackRelatedReferenceSingle(ReferenceBase, APIView):
    resource_attr = None

    @swagger_auto_schema(responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                         **{self.resource_attr: True})
            reference = Reference.objects.get(active=True, feedbacks=feedback_id, feedbacks__user=request.user)
            reports = AnnotationReport.objects.filter(reference_id=reference.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Reference.DoesNotExist):
            return NotFoundResponse()
        return Response(ReferenceSerializer(instance=self.get_pre_serialized_reference(reference, feedback, reports),
                                            context={'request': request}).data)


class AnnotationUpvoteRelatedReferenceSingle(ReferenceFeedbackRelatedReferenceSingle):
    resource_attr = 'upvote'


class AnnotationReportRelatedReferenceSingle(ReferenceBase, APIView):

    @swagger_auto_schema(responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, report_id):
        try:
            AnnotationReport.objects.get(id=report_id, user=request.user)
            reference = Reference.objects.get(annotation_reports=report_id, active=True,
                                              annotation_reports__user=request.user)
            feedback = AnnotationUpvote.objects.get(reference_id=reference.id, user=request.user)
            reports = AnnotationReport.objects.filter(reference_id=reference.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Reference.DoesNotExist, AnnotationReport.DoesNotExist):
            return NotFoundResponse()
        return Response(ReferenceSerializer(instance=self.get_pre_serialized_reference(reference, feedback, reports),
                                            context={'request': request}).data)