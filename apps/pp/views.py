from django.core.paginator import Paginator, EmptyPage
from django.db.models import Case
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Coalesce
from django.http import Http404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lazysignup.decorators import allow_lazy_user
from rest_framework import status
from rest_framework.parsers import JSONParser

from apps.pp.utils import SuccessHttpResponse, ErrorHttpResponse
from .models import Reference, UserReferenceFeedback
from .serializers import ReferencePOSTSerializer, ReferencePATCHSerializer, ReferenceGETSerializer, \
    ReferenceListGETSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ReferenceDetail(View):
    def get_object(self, pk):
        try:
            return Reference.objects.get(pk=pk)
        except Reference.DoesNotExist:
            raise Http404

    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["GET"]))
    def get(self, request, pk):
        reference = self.get_object(pk)
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(serializer.data)


    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["PATCH"]))
    def patch(self, request, pk):
        reference = self.get_object(pk)
        data = JSONParser().parse(request)
        serializer = ReferencePATCHSerializer(reference, context={'request': request}, data=data, partial=True)
        if serializer.is_valid():
            if len(serializer.validated_data) == 0:
                return HttpResponse(status=400)
            serializer.save()
            reference2 = self.get_object(pk)
            serializer2 = ReferenceGETSerializer(reference2, context={'request': request})
            return SuccessHttpResponse(serializer2.data)
        return ErrorHttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["DELETE"]))
    def delete(self, request, pk):
        reference = self.get_object(pk)
        reference.delete()
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(serializer.data, status=status.HTTP_200_OK)


class ReferenceList(View):
    default_page_size = 100
    default_order = "-create_date"

    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["GET"]))
    def get(self, request):
        url = request.GET.get('url')
        order = request.GET.get('order', self.default_order)
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', self.default_page_size)

        query = Reference.objects.order_by(order)
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

        # Manually annotate useful & objection feedbacks for the current user
        reference_ids = set(reference.id for reference in references)
        feedbacks = UserReferenceFeedback.objects.filter(user=request.user, reference_id__in=reference_ids)
        reference_to_feedback = {feedback.reference_id:feedback for feedback in feedbacks}
        for reference in references:
            feedback = reference_to_feedback.get(reference.id)
            if feedback:
                reference.useful = feedback.useful
                reference.objection = feedback.objection

        # Finally pass over the annotated references to the serializer so it makes use of them
        # along with the "native" model fields
        references = ReferenceListGETSerializer(references, context={'request': request}, many=True).data

        data = {'total': paginator.count, 'rows': references}
        return SuccessHttpResponse(data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ReferencePOST(View):
    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request):
        data = JSONParser().parse(request)
        data['user'] = request.user.pk
        serializer = ReferencePOSTSerializer(data=data)
        if serializer.is_valid():
            reference = serializer.save()
            reference_json = ReferenceGETSerializer(reference, context={'request': request})
            return SuccessHttpResponse(reference_json.data, status=status.HTTP_200_OK)

        return ErrorHttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




