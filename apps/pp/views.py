from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user
from rest_framework.renderers import JSONRenderer

from apps.pp.utils import SuccessHttpResponse, ErrorHttpResponse
from .models import Reference
from .serializers import ReferencePOSTSerializer, ReferencePATCHSerializer, ReferenceGETSerializer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ReferenceDetail(View):
    def get_object(self, pk):
        try:
            return Reference.objects.get(pk=pk)
        except Reference.DoesNotExist:
            raise Http404

    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["GET"]))
    def get(self, request, pk, format=None):
        reference = self.get_object(pk)
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(serializer.data)


    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["PATCH"]))
    def patch(self, request, pk, format=None):
        reference = self.get_object(pk)
        data = JSONParser().parse(request)
        serializer = ReferencePATCHSerializer(reference, data=data, partial=True)
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
    def delete(self, request, pk, format=None):
        reference = self.get_object(pk)
        reference.delete()
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return SuccessHttpResponse(serializer.data, status=status.HTTP_200_OK)


class ReferenceList(View):
    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["GET"]))
    def get(self, request, url, format=None):
        references = Reference.objects.filter(url=url).order_by("-create_date")
        references = list(references)
        references.sort(key=lambda ref: ref.create_date, reverse=True)
        total = len(references)
        rows = []
        for i in range(len(references)):
            rows.append(ReferenceGETSerializer(references[i], context={'request': request}).data)
        data = {'total': total, 'rows': rows}
        return SuccessHttpResponse(data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ReferencePOST(View):
    @method_decorator(allow_lazy_user)
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, format=None):
        data = JSONParser().parse(request)
        data['user'] = request.user.pk
        serializer = ReferencePOSTSerializer(data=data)
        if serializer.is_valid():
            reference = serializer.save()
            reference_json = ReferenceGETSerializer(reference)
            return SuccessHttpResponse(reference_json.data, status=status.HTTP_200_OK)

        return ErrorHttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




