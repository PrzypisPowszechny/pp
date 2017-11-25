from django.core.paginator import Paginator, EmptyPage
from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lazysignup.decorators import allow_lazy_user
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from apps.pp.utils import SuccessHttpResponse, ErrorHttpResponse, PermissionDenied
from .models import Reference, UserReferenceFeedback
from .serializers import ReferencePOSTSerializer, ReferencePATCHSerializer, ReferenceGETSerializer, \
    ReferenceListGETSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ReferenceDetail(APIView):
    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["GET"]))
    def get(self, request, pk):
        try:
            reference = Reference.objects.select_related('reference_request').get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorHttpResponse()

        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(serializer.data)

    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["PATCH"]))
    def patch(self, request, pk):
        try:
            reference = Reference.objects.select_related('reference_request').get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorHttpResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()
        data = JSONParser().parse(request)
        serializer = ReferencePATCHSerializer(reference, context={'request': request}, data=data, partial=True)
        if not serializer.is_valid():
            return ErrorHttpResponse(serializer.errors)

        if len(serializer.validated_data) == 0:
            return ErrorHttpResponse()

        serializer.save()

        try:
            updated_reference = Reference.objects.get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorHttpResponse()

        serializer2 = ReferenceGETSerializer(updated_reference, context={'request': request})
        return SuccessHttpResponse(serializer2.data)


    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["DELETE"]))
    def delete(self, request, pk):
        try:
            reference = Reference.objects.select_related('reference_request').get(pk=pk)
        except Reference.DoesNotExist:
            return ErrorHttpResponse()

        # Check permissions
        if reference.user_id != request.user.id:
            return PermissionDenied()

        reference.delete()
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(serializer.data)


class ReferenceList(APIView):
    default_page_size = 10
    default_order = "-create_date"

    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["GET"]))
    def get(self, request):
        url = request.GET.get('url')
        order = request.GET.get('order', self.default_order)
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', self.default_page_size)

        query = Reference.objects.select_related('reference_request').order_by(order)
        if url is not None:
            query = query.filter(url=url)

        # Aggregate eagerly with useful_count and objection_count
        # With any serious number of records such count might be further optimized, e.g. by caching
        # it is here to stay only for a version with limited users
        query = query.filter(user=request.user).annotate(
            useful_count=Coalesce(
                Sum(Case(When(feedbacks__useful=True, then=1)), default=0, output_field=IntegerField()),
                0),
            objection_count=Coalesce(
                Sum(Case(When(feedbacks__objection=True, then=1)), default=0, output_field=IntegerField()),
                0)
        )

        # Paginate the queryset
        paginator = Paginator(query, page_size)
        try:
            references = paginator.page(page)
        except EmptyPage:
            references = paginator.page(paginator.num_pages)

        # Get ids on the current page
        reference_ids = set(reference.id for reference in references)

        # Get references that belong to the user
        user_reference_ids = Reference.objects\
            .filter(user=request.user, id__in=reference_ids).values_list('id', flat=True)

        # Manually annotate useful & objection feedbacks for the current user
        feedbacks = UserReferenceFeedback.objects.filter(user=request.user, reference_id__in=reference_ids)
        reference_to_feedback = {feedback.reference_id:feedback for feedback in feedbacks}
        for reference in references:
            feedback = reference_to_feedback.get(reference.id)
            if feedback:
                reference.useful = feedback.useful
                reference.objection = feedback.objection
                reference.does_belong_to_user = reference.id in user_reference_ids

        # Finally pass over the annotated reference models to the serializer so it makes use of them
        # along with the "native" model fields
        references = ReferenceListGETSerializer(references, context={'request': request}, many=True).data

        data = {'total': paginator.count, 'rows': references}
        return SuccessHttpResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class ReferencePOST(APIView):
    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request):
        data = JSONParser().parse(request)
        data['user'] = request.user.pk
        serializer = ReferencePOSTSerializer(data=data)
        if not serializer.is_valid():
            return ErrorHttpResponse(serializer.errors)
        reference = serializer.save()
        reference_json = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(reference_json.data)





