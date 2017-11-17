import json
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from lazysignup.decorators import allow_lazy_user
from .models import Reference, User, UserReferenceFeedback
from django.core.exceptions import ObjectDoesNotExist
from .serializers import ReferencePOSTSerializer, ReferencePATCHSerializer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView


@allow_lazy_user
def get_view(request, pk):
    # With allow lazy user, a new user is created at database for every request
    try:
        reference = Reference.objects.get(id=pk)
    except Reference.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'GET':
        reference_json = prepare_reference_json(request, pk)
        return HttpResponse(json.dumps(reference_json), content_type='application/json')
    elif request.method == 'PATCH':
        data = JSONParser().parse(request)
        serializer = ReferencePATCHSerializer(reference, data=data, partial=True)
        if serializer.is_valid():
            if len(serializer.validated_data) == 0:
                return HttpResponse(status=400)
            serializer.save()
            reference_json = prepare_reference_json(request, pk)
            return HttpResponse(json.dumps(reference_json), content_type='application/json', status=200)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        reference.delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def prepare_reference_json(request, pk):
    reference = Reference.objects.get(id=pk)
    user = User.objects.get(id=request.user.id)
    urf = UserReferenceFeedback()
    try:
        urf = UserReferenceFeedback.objects.get(user=user, reference=reference)
    except ObjectDoesNotExist:
        urf.useful = False
        urf.objection = False
    reference.count_useful_and_objection()
    reference_json = {
        'id': reference.id,
        'url': reference.url,
        'range': reference.range,
        'quote': reference.quote,
        'priority': reference.priority,
        'link': reference.link,
        'link_title': reference.link_title,
        'useful': urf.useful,
        'useful_count': reference.useful_count,
        'objection': urf.objection,
        'objection_count': reference.objection_count}
    return reference_json


@allow_lazy_user
def search_view(request, url):
    references = Reference.objects.filter(url=url)
    total = references.count()
    references = list(references)
    references.sort(key=lambda ref: ref.create_date, reverse=True)
    rows = []
    for ref in references:
        rows.append(prepare_reference_json(request, ref.id))
    js = {
        'total': total,
        'rows': rows
    }
    return HttpResponse(json.dumps(js), content_type='application/json')


@allow_lazy_user
def post_view(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        data['user'] = request.user.pk
        serializer = ReferencePOSTSerializer(data=data)
        if serializer.is_valid():
            reference = serializer.save()
            reference_json = prepare_reference_json(request, reference.id)
            return HttpResponse(json.dumps(reference_json), content_type='application/json', status=201)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return HttpResponse(content_type='application/json', status=400)
