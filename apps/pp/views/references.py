from apps.pp.utils.views import PermissionDenied, ValidationErrorResponse, ErrorResponse, data_wrapped_view, \
    NotFoundResponse
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
from drf_yasg.utils import swagger_auto_schema


from apps.pp.models import Reference, UserReferenceFeedback, ReferenceRequest
from apps.pp.serializers import ReferencePATCHQuerySerializer, ReferenceListGETSerializer, \
    data_wrapped, ReferenceQuerySerializer, ReferenceSerializer, get_relationship_id, set_relationship


class ReferenceDetail(APIView):
    resource_name = 'references'

    @swagger_auto_schema(responses={200: data_wrapped(ReferenceSerializer)})
    @method_decorator(allow_lazy_user)
    @method_decorator(data_wrapped_view)
    def get(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse('Resource not found')

        attributes_serializer = ReferenceSerializer.Attributes(reference, context={'request': request})
        data = {'id': reference.id, 'type': self.resource_name, 'attributes': attributes_serializer.data}
        set_relationship(data, reference.reference_request_id, cls=ReferenceRequest)
        set_relationship(data, reference.user)
        return data

    @swagger_auto_schema(request_body=data_wrapped(ReferencePATCHQuerySerializer),
                         responses={200: data_wrapped(ReferenceSerializer)})
    @method_decorator(allow_lazy_user)
    @method_decorator(data_wrapped_view)
    def patch(self, request, reference_id):
        try:
            reference = Reference.objects.select_related('reference_request').get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return ErrorResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()
        serializer = ReferencePATCHQuerySerializer(data=request.data, context={'request': request}, partial=True)
        if not serializer.is_valid():
            return ErrorResponse(serializer.errors)

        patched_data = serializer.validated_data.get('attributes', {})
        if not patched_data:
            return ErrorResponse()
        for k, v in patched_data.items():
            setattr(reference, k, v)
        reference.save()

        attributes_serializer = ReferenceSerializer.Attributes(reference, context={'request': request})
        data = {'id': reference.id, 'type': self.resource_name, 'attributes': attributes_serializer.data}
        set_relationship(data, reference.reference_request_id, cls=ReferenceRequest)
        set_relationship(data, reference.user)
        return data

    @method_decorator(allow_lazy_user)
    @method_decorator(data_wrapped_view)
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
        return None


class ReferencePOST(APIView):
    resource_name = 'references'

    @swagger_auto_schema(request_body=data_wrapped(ReferenceQuerySerializer),
                         responses={200: data_wrapped(ReferenceSerializer)})
    @method_decorator(allow_lazy_user)
    @method_decorator(data_wrapped_view)
    def post(self, request):
        query_serializer = ReferenceQuerySerializer(data=request.data)
        if not query_serializer.is_valid():
            return ValidationErrorResponse(query_serializer.errors)
        reference = Reference(**query_serializer.data['attributes'])
        reference.user_id = request.user.pk
        reference.reference_request_id = get_relationship_id(query_serializer, 'reference_request')
        reference.save()

        attributes_serializer = ReferenceSerializer.Attributes(reference, context={'request': request})
        data = {'id': reference.id, 'type': self.resource_name, 'attributes': attributes_serializer.data}
        # alternative for line below: cls=reference._meta.get_field('reference_request').related_model
        set_relationship(data, reference.reference_request_id, cls=ReferenceRequest)
        set_relationship(data, reference.user)
        return data


class ReferenceList(APIView):
    resource_name = 'references'

    pagination_class = LimitOffsetPagination
    default_page_size = 100
    default_sort = "-create_date"

    def get_queryset(self, request):
        queryset = Reference.objects.select_related('reference_request').filter(active=True)
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
    @method_decorator(data_wrapped_view)
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
        data_list = []
        feedbacks = UserReferenceFeedback.objects.filter(user=request.user, reference_id__in=reference_ids)
        reference_to_feedback = {feedback.reference_id: feedback for feedback in feedbacks}
        for reference in references:
            feedback = reference_to_feedback.get(reference.id)
            if feedback:
                reference.useful = feedback.useful
                reference.objection = feedback.objection
                reference.does_belong_to_user = reference.id in user_reference_ids
            attributes_serializer = ReferenceListGETSerializer.Attributes(reference, context={'request': request})
            data = {'id': reference.id, 'type': 'references', 'attributes': attributes_serializer.data}
            set_relationship(data, reference.user_id, cls=reference._meta.get_field('user_id').related_model)
            set_relationship(data, reference.reference_request_id, cls=ReferenceRequest)
            data_list.append(data)
        return data_list
