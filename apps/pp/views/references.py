from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView

from apps.pp.responses import PermissionDenied, ValidationErrorResponse, ErrorResponse, NotFoundResponse
from django.db.models import Case, Prefetch
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema

from apps.pp.models import Reference, UserReferenceFeedback, ReferenceReport
from apps.pp.serializers import ReferencePatchDeserializer, ReferenceListSerializer, ReferenceDeserializer, \
    ReferenceSerializer
from apps.pp.utils import get_relationship_id, set_relationship, get_resource_name, DataPreSerializer


class ReferenceDetail(APIView):
    resource_name = 'references'

    @swagger_auto_schema(responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse('Resource not found')

        data = {'id': reference.id, 'type': self.resource_name, 'attributes': reference}
        set_relationship(data, reference, attr='reference_request_id')
        set_relationship(data, reference.user, attr='id')
        return Response(ReferenceSerializer(data, context={'request': request}).data)

    @swagger_auto_schema(request_body=ReferencePatchDeserializer,
                         responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def patch(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()
        deserializer = ReferencePatchDeserializer(data=request.data, context={'request': request}, partial=True)
        if not deserializer.is_valid():
            return ErrorResponse(deserializer.errors)

        patched_data = deserializer.validated_data.get('attributes', {})
        if not patched_data:
            return ErrorResponse()
        for k, v in patched_data.items():
            setattr(reference, k, v)
        reference.save()

        data = {'id': reference.id, 'type': self.resource_name, 'attributes': reference}
        set_relationship(data, reference, attr='reference_request_id')
        set_relationship(data, reference.user, attr='id')
        return Response(ReferenceSerializer(data, context={'request': request}).data)

    @method_decorator(allow_lazy_user)
    def delete(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(id=reference_id)
        except Reference.DoesNotExist:
            return NotFoundResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()

        if reference.active:
            reference.active = False
            reference.save()
        return Response()


class ReferenceList(GenericAPIView):
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
        reference.reference_request_id = get_relationship_id(deserializer, 'reference_request')
        reference.save()

        data = {'id': reference.id, 'type': self.resource_name, 'attributes': reference}
        set_relationship(data, reference, attr='reference_request_id')
        set_relationship(data, reference.user, attr='id')
        return Response(ReferenceSerializer(data, context={'request': request}).data)

    def get_queryset(self):
        queryset = Reference.objects \
            .select_related('reference_request') \
            .filter(active=True).annotate(
                useful_count=Coalesce(
                    Sum(Case(When(feedbacks__useful=True, then=1)), default=0, output_field=IntegerField()),
                    0),
                objection_count=Coalesce(
                    Sum(Case(When(feedbacks__objection=True, then=1)), default=0, output_field=IntegerField()),
                    0)
            ).prefetch_related(
                Prefetch('reference_reports', queryset=ReferenceReport.objects.filter(user=self.request.user),
                         to_attr='user_reference_reports')
            )
        return queryset

    def annotate_fetched_queryset(self, queryset):
        # Get ids on the current page
        reference_ids = set(reference.id for reference in queryset)

        # Get references that belong to the user
        user_reference_ids = Reference.objects \
            .filter(user=self.request.user, id__in=reference_ids).values_list('id', flat=True)

        # Manually annotate useful & objection feedbacks for the current user
        feedbacks = UserReferenceFeedback.objects.filter(user=self.request.user, reference_id__in=reference_ids)
        reference_to_feedback = {feedback.reference_id: feedback for feedback in feedbacks}
        for reference in queryset:
            feedback = reference_to_feedback.get(reference.id)
            if feedback:
                # TODO: setting useful and objection attrs duplicates corresponding relationships, consider removing
                reference.useful = feedback.useful
                reference.objection = feedback.objection
                reference.does_belong_to_user = reference.id in user_reference_ids
            reference.user_feedback = feedback
        return queryset

    def pre_serialize_queryset(self, queryset):
        data_list = []
        for reference in queryset:
            data = {'attributes': reference}
            pre_serializer = DataPreSerializer(reference, data)
            pre_serializer.set_relation(get_resource_name(reference, related_field='reference_request_id'),
                                        resource_id=reference.reference_request_id)
            pre_serializer.set_relation(get_resource_name(reference.user),
                                        resource_id=reference.user.id)
            pre_serializer.set_relation(get_resource_name(reference.user_feedback, model=UserReferenceFeedback),
                                        resource_id=reference.user_feedback)
            pre_serializer.set_relation(get_resource_name(reference, related_field='reference_reports'),
                                        resource_id=reference.user_reference_reports)
            data_list.append(pre_serializer.data)
        return data_list

    @swagger_auto_schema(responses={200: ReferenceListSerializer(many=True)})
    @method_decorator(allow_lazy_user)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.paginator.paginate_queryset(queryset, request)

        queryset = self.annotate_fetched_queryset(queryset)

        data_list = self.pre_serialize_queryset(queryset)

        return self.get_paginated_response(ReferenceListSerializer(data_list, many=True).data)
