from django.core.signing import Signer, BadSignature
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.conf import settings

from apps.annotation.models import AnnotationRequest
from .http_basicauth import logged_in_or_basicauth


@logged_in_or_basicauth()
def site_test_index(request):
    return render(request, 'site/site_test_index.html')


def report_form(request):
    return render(request, 'site/report_form.html')


def about(request):
    return redirect('https://facebook.com/przypis.powszechny/', permanent=True)


def annotation_request_unsubscribe(request, annotation_request_id, token):
    try:
        instance = AnnotationRequest.objects.get(id=annotation_request_id)
    except AnnotationRequest.DoesNotExist:
        return Http404()
    try:
        signature = '{}:{}'.format(annotation_request_id, token)
        Signer().unsign(signature)
    except BadSignature:
        return HttpResponseBadRequest('Bad token')

    instance.notification_email = ''
    instance.save()

    return render_to_response('site/unsubscribed.html')


def social_login_demo(request):
    if settings.ENV == 'prod':
        raise Http404()
    return render(request, 'site/social_login_demo.html')
