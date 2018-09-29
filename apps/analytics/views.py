from logging import getLogger

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from . import ga

logger = getLogger('pp.analytics')


@csrf_exempt
def init_ping(request):
    """
    View called by extension every time it starts, this is hook for things like setting cookies etc
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method accepted')

    response = HttpResponse()

    # Set GA cookies, based on send data
    cookies = ga.set_cookies(request.POST)
    if not cookies:
        logger.info('No cookie data extracted from POST in init_ping')
    for cookie in cookies:
        response.set_cookie(**cookie)
    return response


def extension_uninstalled_event(request):
    cid_value = ga.read_cid_from_cookie(request)
    if cid_value is None:
        logger.error('Cid cookie not set or malformed.')
    else:
        ga.send_event_extension_uninstalled(cid_value)
    return render_to_response('analytics.html')
