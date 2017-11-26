from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from lazysignup.decorators import allow_lazy_user
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.pp.utils.responses import PermissionDenied, ValidationErrorResponse, ErrorResponse
from .models import Reference, UserReferenceFeedback
from .serializers import ReferencePATCHSerializer, ReferenceGETSerializer, \
    ReferenceListGETSerializer, ReferencePOSTSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ReferenceDetail(APIView):
    resource_name = 'references'

    @method_decorator(allow_lazy_user)
    def get(self, request, pk):
        try:
            reference = Reference.objects.select_related('reference_request').get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorResponse('Resource not found')

        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return Response(serializer.data)

    @method_decorator(allow_lazy_user)
    def patch(self, request, pk):
        try:
            reference = Reference.objects.select_related('reference_request').get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()
        data = JSONParser().parse(request)
        serializer = ReferencePATCHSerializer(reference, context={'request': request}, data=data, partial=True)
        if not serializer.is_valid():
            return ErrorResponse(serializer.errors)

        if len(serializer.validated_data) == 0:
            return ErrorResponse()

        serializer.save()

        try:
            updated_reference = Reference.objects.get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorResponse()

        serializer2 = ReferenceGETSerializer(updated_reference, context={'request': request})
        return Response(serializer2.data)

    @method_decorator(allow_lazy_user)
    def delete(self, request, pk):
        try:
            reference = Reference.objects.select_related('reference_request').get(pk=pk)
        except Reference.DoesNotExist:
            return Response()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()

        reference.delete()
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ReferencePOST(APIView):
    resource_name = 'references'

    @method_decorator(allow_lazy_user)
    def post(self, request):
        data = JSONParser().parse(request)
        data['user'] = request.user.pk
        serializer = ReferencePOSTSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
        reference = serializer.save()
        reference_json = ReferenceGETSerializer(reference, context={'request': request})
        return Response(reference_json.data)


class ReferenceList(APIView):
    resource_name = 'references'

    pagination_class = LimitOffsetPagination
    default_page_size = 100
    default_sort = "-create_date"

    def get_queryset(self):
        queryset = Reference.objects.select_related('reference_request')

        sort = self.kwargs.get('sort', self.default_sort)
        if sort:
            queryset = queryset.order_by(sort)

        url = self.kwargs.get('url')
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
        queryset = self.get_queryset()

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