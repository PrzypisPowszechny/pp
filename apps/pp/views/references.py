from apps.pp.utils.views import PermissionDenied, ValidationErrorResponse, ErrorResponse
from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination
from rest_framework_json_api.parsers import JSONParser

from apps.pp.models import Reference, UserReferenceFeedback
from apps.pp.serializers import ReferencePATCHSerializer, ReferenceListGETSerializer, ReferenceSerializer
from apps.pp.utils.views import get_data_fk_value

import logging;

class ReferenceDetail(APIView):
    resource_name = 'references'

    @method_decorator(allow_lazy_user)
    def get(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse('Resource not found')

        serializer = ReferenceSerializer(reference, context={'request': request})
        return Response(serializer.data)

    @method_decorator(allow_lazy_user)
    def patch(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()
        data = JSONParser().parse(request, parser_context={'request': request, 'view': ReferencePOST})
        serializer = ReferencePATCHSerializer(reference, context={'request': request}, data=data, partial=True)
        if not serializer.is_valid():
            return ErrorResponse(serializer.errors)

        if len(serializer.validated_data) == 0:
            return ErrorResponse()

        serializer.save()

        try:
            updated_reference = Reference.objects.get(id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse()

        serializer2 = ReferenceSerializer(updated_reference, context={'request': request})
        return Response(serializer2.data)

    @method_decorator(allow_lazy_user)
    def delete(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return Response()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()

        reference.active = False
        reference.save()
        serializer = ReferenceSerializer(reference, context={'request': request})
        return Response(serializer.data)


class ReferencePOST(APIView):
    resource_name = 'references'

    @method_decorator(allow_lazy_user)
    def post(self, request):
        data = JSONParser().parse(request, parser_context={'request': request, 'view': ReferencePOST})
        # KG: we need to help JSONParser with relationships: extract {'id': X} pairs to X
        data['reference_request'] = get_data_fk_value(data, 'reference_request')
        # Set the user as the authenticated user
        data['user'] = request.user.pk

        serializer = ReferenceSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
        reference = serializer.save()
        reference_json = ReferenceSerializer(reference, context={'request': request})
        return Response(reference_json.data)


class ReferenceList(APIView):
    resource_name = 'references'

    pagination_class = LimitOffsetPagination
    default_page_size = 100
    default_sort = "-create_date"

    def get_queryset(self, request):
        queryset = Reference.objects.select_related('reference_request').filter(active=True)
        print(request.query_params.get('sort'))
        sort = request.query_params.get('sort', self.default_sort)
        if sort:
            queryset = queryset.order_by(sort)

        url = request.query_params.get('url')
        if url:
            queryset = queryset.filter(url=url)

        # Aggregate eagerly with useful_count and objection_count
        # With any serious number of records such count might be further optimized, e.g. by caching
        # it is here to stay only for a version with limited users
        queryset = queryset.annotate(
            useful_count=Coalesce(
                Sum(Case(When(feedbacks__useful=True, then=1)), default=0, output_field=IntegerField()),
                0),
            objection_count=Coalesce(
                Sum(Case(When(feedbacks__objection=True, then=1)), default=0, output_field=IntegerField()),
                0)
        )
        return queryset

    @method_decorator(allow_lazy_user)
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)

        # Paginate the queryset
        references = LimitOffsetPagination().paginate_queryset(queryset, request)

        # Get ids on the current page
        reference_ids = set(reference.id for reference in references)

        # Get references that belong to the user
        user_reference_ids = Reference.objects \
            .filter(user=request.user, id__in=reference_ids).values_list('id', flat=True)

        # Manually annotate useful & objection feedbacks for the current user
        feedbacks = UserReferenceFeedback.objects.filter(user=request.user, reference_id__in=reference_ids)
        reference_to_feedback = {feedback.reference_id: feedback for feedback in feedbacks}
        for reference in references:
            feedback = reference_to_feedback.get(reference.id)
            if feedback:
                reference.useful = feedback.useful
                reference.objection = feedback.objection
                reference.does_belong_to_user = reference.id in user_reference_ids

        # Finally pass over the annotated reference models to the serializer so it makes use of them
        # along with the "native" model fields
        references = ReferenceListGETSerializer(references, context={'request': request}, many=True).data

        return Response(references)
