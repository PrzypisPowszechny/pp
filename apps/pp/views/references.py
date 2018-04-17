from django.db.models import Case
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

from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.serializers import ReferencePatchDeserializer, ReferenceListSerializer, ReferenceDeserializer, \
    ReferenceSerializer, get_relationship_id, set_relationship
from apps.pp.utils.views import PermissionDenied, ValidationErrorResponse, ErrorResponse, NotFoundResponse


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

    @swagger_auto_schema(request_body=ReferenceDeserializer,
                         responses={200: ReferenceSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        query_serializer = ReferenceDeserializer(data=request.data)
        if not query_serializer.is_valid():
            return ValidationErrorResponse(query_serializer.errors)
        reference = Reference(**query_serializer.validated_data['attributes'])
        reference.user_id = request.user.pk
        reference.reference_request_id = get_relationship_id(query_serializer, 'reference_request')
        reference.save()

        data = {'id': reference.id, 'type': self.resource_name, 'attributes': reference}
        set_relationship(data, reference, attr='reference_request_id')
        set_relationship(data, reference.user, attr='id')
        return Response(ReferenceSerializer(data, context={'request': request}).data)


class ReferenceList(GenericAPIView):
    resource_name = 'references'
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"
    filter_fields = ('url',)

    def get_queryset(self):
        queryset = Reference.objects.select_related('reference_request').filter(active=True).annotate(
            useful_count=Coalesce(
                Sum(Case(When(feedbacks__useful=True, then=1)), default=0, output_field=IntegerField()),
                0),
            objection_count=Coalesce(
                Sum(Case(When(feedbacks__objection=True, then=1)), default=0, output_field=IntegerField()),
                0)
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
                reference.useful = feedback.useful
                reference.objection = feedback.objection
                reference.does_belong_to_user = reference.id in user_reference_ids
        return queryset

    def preserialize_queryset(self, queryset):
        data_list = []
        for reference in queryset:
            attributes_serializer = ReferenceListSerializer.Attributes(reference, context={'request': self.request})
            data = {'id': reference.id, 'type': 'references', 'attributes': attributes_serializer.data}
            set_relationship(data, reference, attr='reference_request_id')
            set_relationship(data, reference.user, attr='id')
            data_list.append(data)
        return data_list

    @swagger_auto_schema(responses={200: ReferenceListSerializer(many=True)})
    @method_decorator(allow_lazy_user)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.paginator.paginate_queryset(queryset, request)

        queryset = self.annotate_fetched_queryset(queryset)

        data_list = self.preserialize_queryset(queryset)

        return self.get_paginated_response(ReferenceListSerializer(data_list, many=True).data)
