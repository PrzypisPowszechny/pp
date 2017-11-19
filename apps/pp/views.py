from rest_framework import status
from django.http import HttpResponse, JsonResponse
from lazysignup.decorators import allow_lazy_user
from .models import Reference
from .serializers import ReferencePOSTSerializer, ReferencePATCHSerializer, ReferenceGETSerializer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from django.utils.decorators import method_decorator


class ReferenceDetail(APIView):
    def get_object(self, pk):
        try:
            return Reference.objects.get(pk=pk)
        except Reference.DoesNotExist:
            raise Http404

    @method_decorator(allow_lazy_user)
    def get(self, request, pk, format=None):
        reference = self.get_object(pk)
        serializer = ReferenceGETSerializer(reference, context={'request': request})
        return Response(serializer.data)

    @method_decorator(allow_lazy_user)
    def patch(self, request, pk, format=None):
        reference = self.get_object(pk)
        serializer = ReferencePATCHSerializer(reference, data=request.data, partial=True)
        if serializer.is_valid():
            if len(serializer.validated_data) == 0:
                return HttpResponse(status=400)
            serializer.save()
            reference2 = self.get_object(pk)
            serializer2 = ReferenceGETSerializer(reference2, context={'request': request})
            return Response(serializer2.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(allow_lazy_user)
    def delete(self, request, pk, format=None):
        reference = self.get_object(pk)
        reference.delete()
        return Response(status=status.HTTP_200_OK)


class ReferenceList(APIView):
    @method_decorator(allow_lazy_user)
    def get(self, request, url, format=None):
        references = Reference.objects.filter(url=url).order_by("-create_date")
        references = list(references)
        references.sort(key=lambda ref: ref.create_date, reverse=True)
        total = len(references)
        rows = []
        for i in range(len(references)):
            rows.append(ReferenceGETSerializer(references[i], context={'request': request}).data)
        data = {'total': total, 'rows': rows}
        return Response(data)


class ReferencePOST(APIView):
    @method_decorator(allow_lazy_user)
    def post(self, request, format=None):
        data = JSONParser().parse(request)
        data['user'] = request.user.pk
        serializer = ReferencePOSTSerializer(data=data)
        if serializer.is_valid():
            reference = serializer.save()
            reference_json = ReferenceGETSerializer(reference)
            return Response(reference_json.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
