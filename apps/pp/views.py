import json
from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user
from .models import Reference, User, UserReferenceFeedback
from django.core.exceptions import ObjectDoesNotExist


@allow_lazy_user
def get_view(request, pk):
    # With allow lazy user, a new user is created at database for every request
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
    return HttpResponse(json.dumps(reference_json), content_type='application/json')

